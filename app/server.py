"""Local-only assessment server. Standard library runtime; no keys in frontend."""

import base64, hashlib, hmac, io, json, os, secrets, threading, time, urllib.error, urllib.request, uuid, wave
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit
from .kb import ROOT, KnowledgeBase, redact
from .agent import Agent
from .nudges import NudgeEngine


def load_env():
    path = ROOT / ".env"
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip() and not line.lstrip().startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_env()
KB = KnowledgeBase()
SESSIONS = {}
LOCK = threading.RLock()
TOKEN = secrets.token_urlsafe(32)
LOCALES = {"en-PH": "PH", "fil-PH": "PH", "id-ID": "ID"}


def transcribe(audio, language):
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        raise ValueError(
            "Audio ASR is not configured. Add OPENAI_API_KEY in your local .env and restart."
        )
    try:
        with wave.open(io.BytesIO(audio)) as wav:
            if (
                wav.getnchannels() != 1
                or not 8000 <= wav.getframerate() <= 96000
                or wav.getsampwidth() != 2
                or wav.getnframes() / wav.getframerate() > 12
            ):
                raise ValueError("Expected mono PCM16 WAV, at most 12 seconds.")
    except (wave.Error, EOFError):
        raise ValueError("Invalid WAV audio.")
    boundary = "bridge" + uuid.uuid4().hex
    parts = []
    for keyname, val in {
        "model": os.environ.get("ASR_MODEL", "gpt-4o-mini-transcribe"),
        "language": {"en-PH": "en", "fil-PH": "tl", "id-ID": "id"}[language],
        "response_format": "json",
    }.items():
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{keyname}"\r\n\r\n{val}\r\n'.encode()
        )
    parts.append(
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="chunk.wav"\r\nContent-Type: audio/wav\r\n\r\n'.encode()
        + audio
        + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode())
    req = urllib.request.Request(
        "https://api.openai.com/v1/audio/transcriptions",
        b"".join(parts),
        {
            "Authorization": "Bearer " + key,
            "Content-Type": "multipart/form-data; boundary=" + boundary,
        },
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        raise ValueError(
            f"ASR provider returned HTTP {exc.code}. Check account access and model configuration."
        )
    except (urllib.error.URLError, TimeoutError):
        raise ValueError(
            "ASR timed out or could not connect. Retry after checking connectivity."
        )
    return result["text"], (time.perf_counter() - start) * 1000


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send(self, status, value, kind="application/json"):
        payload = (
            json.dumps(value, ensure_ascii=False).encode()
            if kind == "application/json"
            else value
        )
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(payload)

    def allowed(self):
        host = self.headers.get("Host", "")
        port = self.server.server_port
        return host in {f"localhost:{port}", f"127.0.0.1:{port}"}

    def do_GET(self):
        if not self.allowed():
            return self.send(403, {"error": "Local access only"})
        path = urlsplit(self.path).path
        if path == "/api/config":
            return self.send(
                200,
                {
                    "token": TOKEN,
                    "asr_configured": bool(os.environ.get("OPENAI_API_KEY")),
                    "model": os.environ.get("ASR_MODEL", "gpt-4o-mini-transcribe"),
                },
            )
        if path == "/api/health":
            return self.send(200, {"status": "ok", "records": len(KB.records)})
        files = {"/": "index.html", "/app.js": "app.js", "/style.css": "style.css"}
        if path not in files:
            return self.send(404, {"error": "Not found"})
        filename = files[path]
        kind = {
            "html": "text/html; charset=utf-8",
            "js": "text/javascript; charset=utf-8",
            "css": "text/css; charset=utf-8",
        }[filename.split(".")[-1]]
        return self.send(200, (ROOT / "web" / filename).read_bytes(), kind)

    def do_POST(self):
        try:
            if not self.allowed() or not hmac.compare_digest(
                self.headers.get("X-Bridge-Token", ""), TOKEN
            ):
                return self.send(
                    403,
                    {
                        "error": "Reload the local application to authorize this request."
                    },
                )
            origin = self.headers.get("Origin")
            if origin and origin not in {
                f"http://localhost:{self.server.server_port}",
                f"http://127.0.0.1:{self.server.server_port}",
            }:
                return self.send(403, {"error": "Origin denied"})
            size = int(self.headers.get("Content-Length", 0))
            if not 0 < size < 2_000_000:
                raise ValueError("Request must be between 1 byte and 2 MB")
            body = json.loads(self.rfile.read(size))
            path = urlsplit(self.path).path
            language = body.get("language", "en-PH")
            if language not in LOCALES:
                raise ValueError("Unsupported language")
            if path == "/api/session":
                with LOCK:
                    expired = [
                        k
                        for k, v in SESSIONS.items()
                        if time.monotonic() - v["created"] > 3600
                    ]
                    for k in expired:
                        del SESSIONS[k]
                    if len(SESSIONS) >= 100:
                        raise ValueError(
                            "Session limit reached; restart the local demo"
                        )
                    sid = uuid.uuid4().hex
                    agent = Agent(KB, LOCALES[language], language)
                    opening = agent.respond("")
                    engine = NudgeEngine()
                    if not body.get("coach"):
                        engine.process(opening["assistant"], "agent")
                    SESSIONS[sid] = {
                        "agent": agent,
                        "nudges": engine,
                        "created": time.monotonic(),
                        "lock": threading.Lock(),
                        "chunks": set(),
                    }
                return self.send(200, {"session": sid, "opening": opening})
            if path == "/api/search":
                return self.send(
                    200,
                    {
                        "results": KB.search(
                            str(body.get("text", ""))[:2000],
                            LOCALES[language],
                            language,
                        )
                    },
                )
            session = SESSIONS.get(body.get("session"))
            if not session:
                raise ValueError("Unknown or expired session; start a new call")
            with session["lock"]:
                if path == "/api/turn":
                    text = body.get("text", "")
                    if not isinstance(text, str) or len(text) > 2000:
                        raise ValueError("Turn text too long")
                    answer = session["agent"].respond(text)
                    return self.send(200, answer)
                if path == "/api/analyze" or path == "/api/audio":
                    started = time.perf_counter()
                    asr_ms = None
                    confidence = float(body.get("confidence", 1.0))
                    if not 0 <= confidence <= 1:
                        raise ValueError("Confidence outside [0, 1]")
                    speaker = body.get("speaker", "customer")
                    if speaker not in ("customer", "agent"):
                        raise ValueError("Invalid speaker")
                    if path == "/api/audio":
                        chunk_id = str(body.get("chunk_id", ""))
                        if not chunk_id or chunk_id in session["chunks"]:
                            raise ValueError("Missing or duplicate chunk ID")
                        if len(session["chunks"]) >= 1000:
                            raise ValueError("Start a new call after 1000 chunks")
                        audio = base64.b64decode(body["audio"], validate=True)
                        text, asr_ms = transcribe(audio, session["agent"].language)
                        session["chunks"].add(chunk_id)
                        # Provider has no calibrated confidence here. 1 is rule input, not ASR accuracy.
                        confidence = 1.0
                    else:
                        text = str(body.get("text", ""))[:2000]
                    text = redact(text)
                    result = session["nudges"].process(text, speaker, confidence)
                    result.update(
                        {
                            "text": text,
                            "asr_ms": asr_ms,
                            "confidence_source": (
                                "unavailable" if asr_ms is not None else "test_input"
                            ),
                            "server_ms": (time.perf_counter() - started) * 1000,
                            "mode": "live_audio" if asr_ms is not None else "text_only",
                        }
                    )
                    return self.send(200, result)
                if path == "/api/export":
                    return self.send(
                        200,
                        {
                            "language": session["agent"].language,
                            "turns": session["agent"].events,
                            "nudges": session["nudges"].history,
                            "action": session["agent"].action,
                        },
                    )
            return self.send(404, {"error": "Not found"})
        except (ValueError, KeyError, TypeError) as exc:
            self.send(400, {"error": str(exc)[:250]})
        except Exception:
            self.send(
                500,
                {
                    "error": "Unexpected server error. Restart and use the text fallback."
                },
            )


def main():
    port = int(os.environ.get("PORT", "8765"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Bridgecall ready: http://localhost:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    main()
