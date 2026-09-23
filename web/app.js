"use strict";
const $ = (id) => document.getElementById(id);
let config,
  session = null,
  coach = null,
  busy = false,
  recognition = null,
  live = false,
  context = null,
  mic = null,
  processor = null,
  gain = null;
let samples = [],
  sampleCount = 0,
  windowStart = 0,
  windowSpeaker = "customer",
  queue = [],
  processing = false,
  allAudio = [],
  metrics = [],
  observations = [],
  activeNudges = [];
let callRecorder = null,
  callMic = null,
  callChunks = [];
const locale = () => $("language").value;
function err(e) {
  $("error").textContent = e.message || String(e);
  $("error").hidden = false;
  setTimeout(() => ($("error").hidden = true), 10000);
}
async function api(path, body) {
  const r = await fetch("/api/" + path, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Bridge-Token": config.token,
    },
    body: JSON.stringify(body),
  });
  const data = await r.json();
  if (!r.ok) throw Error(data.error || "Request failed");
  return data;
}
function download(blob, name) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 10000);
}
function jsonDownload(data, name) {
  download(
    new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }),
    name,
  );
}
function bubble(role, text, citation) {
  const b = document.createElement("div");
  b.className = "bubble " + role;
  const s = document.createElement("span");
  s.className = "speaker";
  s.textContent = role;
  b.append(s, document.createTextNode(text));
  if (citation) {
    const c = document.createElement("span");
    c.className = "citation";
    c.textContent = `SOURCE ${citation.record_id} · v${citation.version} · ${citation.source}`;
    b.append(c);
  }
  $("conversation").append(b);
  $("conversation").scrollTop = $("conversation").scrollHeight;
}
function voiceFor(lang) {
  const voices = window.speechSynthesis?.getVoices() || [];
  return (
    voices.find((v) => v.lang.toLowerCase() === lang.toLowerCase()) ||
    voices.find((v) =>
      lang === "fil-PH"
        ? /^(fil|tl)(-|$)/i.test(v.lang)
        : lang === "id-ID"
          ? /^id(-|$)/i.test(v.lang)
          : /^en(-|$)/i.test(v.lang),
    )
  );
}
function speak(text) {
  if (!$("tts").checked) return;
  const voice = voiceFor(locale());
  if (!voice) {
    $("voicestatus").textContent =
      "No matching TTS voice installed for " +
      locale() +
      ". Response remains available as text.";
    return;
  }
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.voice = voice;
  u.lang = voice.lang;
  u.rate = 0.95;
  speechSynthesis.speak(u);
  $("voicestatus").textContent =
    `TTS: ${voice.name} (${voice.lang}). ASR: browser SpeechRecognition; backend/model not exposed.`;
}
async function newCall() {
  if (live || processing || busy || callRecorder?.state === "recording")
    throw Error("Stop recording, finish pending work, then start a new call.");
  speechSynthesis?.cancel();
  recognition?.abort();
  const data = await api("session", { language: locale() });
  session = data.session;
  $("conversation").replaceChildren();
  bubble("assistant", data.opening.assistant);
  $("stage").textContent = data.opening.state;
  speak(data.opening.assistant);
}
async function turn(text) {
  if (busy) return;
  if (!text.trim()) return;
  if (!session) await newCall();
  busy = true;
  try {
    bubble("customer", text);
    const r = await api("turn", { session, language: locale(), text });
    bubble("assistant", r.assistant, r.citation);
    $("stage").textContent = r.state;
    speak(r.assistant);
  } finally {
    busy = false;
  }
}
$("newcall").onclick = () => newCall().catch(err);
$("language").onchange = async () => {
  if (live || processing) {
    $("language").value =
      observations.find((o) => o.mode === "live_audio")?.language || "en-PH";
    err(Error("Stop the live session before changing language."));
    return;
  }
  session = null;
  coach = null;
  speechSynthesis?.cancel();
  recognition?.abort();
  $("stage").textContent = "Start new call";
};
$("turnform").onsubmit = (e) => {
  e.preventDefault();
  const text = $("utterance").value;
  $("utterance").value = "";
  turn(text).catch(err);
};
$("export").onclick = async () => {
  try {
    if (!session) throw Error("Start a call first");
    const data = await api("export", { session });
    jsonDownload(
      {
        ...data,
        evidence_type: "interactive_session",
        tts_voice: voiceFor(locale())?.name || null,
        asr: "Browser SpeechRecognition if used; provider model not exposed",
      },
      "call-transcript-" + session + ".json",
    );
  } catch (e) {
    err(e);
  }
};
for (const b of document.querySelectorAll("[data-example]"))
  b.onclick = () => {
    $("utterance").value = b.dataset.example;
  };
for (const b of document.querySelectorAll("[data-tab]"))
  b.onclick = () => {
    for (const p of document.querySelectorAll(".panel"))
      p.classList.toggle("active", p.id === b.dataset.tab);
    for (const t of document.querySelectorAll("[data-tab]"))
      t.classList.toggle("selected", t === b);
  };
$("speak").onclick = async () => {
  try {
    if (live) throw Error("Stop Live Insights before using the voice bot.");
    if (!session) await newCall();
    speechSynthesis.cancel();
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR)
      throw Error(
        "Speech recognition is unavailable. Use a supported browser or type your response.",
      );
    recognition = new SR();
    recognition.lang = locale() === "fil-PH" ? "fil-PH" : locale();
    recognition.interimResults = false;
    recognition.continuous = false;
    $("speak").disabled = true;
    $("voicestatus").textContent =
      "Listening… Browser speech service may send audio to its provider.";
    recognition.onresult = (e) => turn(e.results[0][0].transcript).catch(err);
    recognition.onerror = (e) =>
      err(Error("Speech recognition: " + e.error + ". You can type instead."));
    recognition.onend = () => {
      $("speak").disabled = false;
    };
    recognition.start();
  } catch (e) {
    $("speak").disabled = false;
    err(e);
  }
};
$("searchform").onsubmit = async (e) => {
  e.preventDefault();
  try {
    const { results } = await api("search", {
      text: $("query").value,
      language: locale(),
    });
    $("results").replaceChildren();
    if (!results.length) {
      $("results").textContent = "No supported record found.";
      return;
    }
    for (const r of results) {
      const el = document.createElement("article");
      el.className = "result";
      const meta = document.createElement("small");
      meta.textContent = `${r.category.toUpperCase()} / ${r.language} / score ${r.score}`;
      const h = document.createElement("h3");
      h.textContent = r.title;
      const p = document.createElement("p");
      p.textContent = r.content;
      const source = document.createElement("small");
      source.textContent = `${r.source} · v${r.version} · SHA256 ${r.content_sha256.slice(0, 12)}`;
      el.append(meta, h, p, source);
      $("results").append(el);
    }
  } catch (e) {
    err(e);
  }
};
async function coachSession() {
  if (!coach) {
    const r = await api("session", { language: locale(), coach: true });
    coach = r.session;
  }
  return coach;
}
$("resetcoach").onclick = () => {
  if (live || processing) {
    err(Error("Stop and finish live audio first."));
    return;
  }
  coach = null;
  activeNudges = [];
  metrics = [];
  observations = [];
  $("streamlog").replaceChildren();
  renderNudges();
  renderMetrics();
};
function log(text) {
  const p = document.createElement("p");
  p.textContent = text;
  $("streamlog").append(p);
  $("streamlog").scrollTop = $("streamlog").scrollHeight;
}
function renderNudges() {
  activeNudges = activeNudges.filter((n) => n.ui_expiry > performance.now());
  $("nudges").replaceChildren();
  if (!activeNudges.length) {
    const p = document.createElement("p");
    p.className = "empty";
    p.textContent = "No active nudges.";
    $("nudges").append(p);
  }
  for (const n of activeNudges) {
    const d = document.createElement("div");
    d.className = "nudge" + (n.priority >= 90 ? " high" : "");
    const h = document.createElement("strong");
    h.textContent = n.topic + " · priority " + n.priority;
    const p = document.createElement("p");
    p.textContent = n.message;
    const e = document.createElement("small");
    e.textContent =
      "Evidence: “" +
      n.evidence +
      "” · expires in " +
      Math.ceil((n.ui_expiry - performance.now()) / 1000) +
      "s";
    d.append(h, p, e);
    $("nudges").append(d);
  }
}
setInterval(renderNudges, 1000);
function percentile(xs, p) {
  const a = [...xs].sort((x, y) => x - y);
  return a.length ? a[Math.max(0, Math.ceil(p * a.length) - 1)] : null;
}
function renderMetrics() {
  const m = metrics.filter((x) => x.mode === "live_audio");
  for (const [id, p] of [
    ["p50", 0.5],
    ["p95", 0.95],
  ]) {
    const value = percentile(
      m.map((x) => x.capture_to_display_ms),
      p,
    );
    $(id).textContent = value === null ? "—" : (value / 1000).toFixed(2) + "s";
  }
  $("metricsnote").textContent = m.length
    ? `${m.length} live audio chunks measured; percentiles include chunks with no nudge.`
    : "No live-audio observations yet. Text timing is exported separately.";
}
async function showAnalysis(r, start, sent, speaker) {
  for (const n of r.nudges) {
    activeNudges = activeNudges.filter((x) => x.topic !== n.topic);
    activeNudges.push({ ...n, ui_expiry: performance.now() + n.ttl_ms });
  }
  renderNudges();
  log(
    `[${r.mode} / ${speaker}] ${r.text || "(empty transcript)"}${r.suppressed ? " — " + r.suppressed : ""}`,
  );
  await new Promise((resolve) =>
    requestAnimationFrame(() => requestAnimationFrame(resolve)),
  );
  const displayed = performance.now();
  const row = {
    mode: r.mode,
    language: locale(),
    speaker,
    asr_ms: r.asr_ms,
    signal_ms: r.signal_ms,
    llm_ms: r.llm_ms || 0,
    llm_used: false,
    delivery_residual_ms: Math.max(0, displayed - sent - r.server_ms),
    capture_to_display_ms: displayed - start,
    window_ms: sent - start,
    nudge_count: r.nudges.length,
  };
  metrics.push(row);
  observations.push({ ...r, language: locale(), speaker, client_metrics: row });
  renderMetrics();
}
$("analyzeform").onsubmit = async (e) => {
  e.preventDefault();
  try {
    const start = performance.now(),
      speaker = $("speaker").value;
    const r = await api("analyze", {
      session: await coachSession(),
      text: $("signaltext").value,
      speaker,
      confidence: $("uncertain").checked ? 0.4 : 1,
    });
    await showAnalysis(r, start, start, speaker);
  } catch (e) {
    err(e);
  }
};
function wavBlob(chunks, rate) {
  const total = chunks.reduce((n, c) => n + c.length, 0);
  const b = new ArrayBuffer(44 + total * 2),
    v = new DataView(b);
  const str = (o, s) => {
    for (let i = 0; i < s.length; i++) v.setUint8(o + i, s.charCodeAt(i));
  };
  str(0, "RIFF");
  v.setUint32(4, 36 + total * 2, true);
  str(8, "WAVE");
  str(12, "fmt ");
  v.setUint32(16, 16, true);
  v.setUint16(20, 1, true);
  v.setUint16(22, 1, true);
  v.setUint32(24, rate, true);
  v.setUint32(28, rate * 2, true);
  v.setUint16(32, 2, true);
  v.setUint16(34, 16, true);
  str(36, "data");
  v.setUint32(40, total * 2, true);
  let offset = 44;
  for (const c of chunks)
    for (const x of c) {
      v.setInt16(offset, Math.max(-1, Math.min(1, x)) * 32767, true);
      offset += 2;
    }
  return new Blob([b], { type: "audio/wav" });
}
function base64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(",")[1]);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}
function flushWindow() {
  if (!sampleCount) return;
  const chunk = samples,
    rate = context.sampleRate,
    start = windowStart,
    speaker = windowSpeaker;
  let energy = 0;
  for (const c of chunk) for (const x of c) energy += x * x;
  const rms = Math.sqrt(energy / sampleCount);
  samples = [];
  sampleCount = 0;
  windowStart = performance.now();
  windowSpeaker = $("speaker").value;
  if (rms < 0.008) {
    log("Silence/low-energy window suppressed before ASR.");
    observations.push({
      mode: "suppressed_audio",
      reason: "rms_below_0.008",
      rms,
    });
    return;
  }
  if (queue.length >= 3) {
    log("Audio queue full — dropped window; restart after provider recovers.");
    observations.push({ mode: "dropped_audio", reason: "queue_full" });
    return;
  }
  queue.push({ blob: wavBlob(chunk, rate), start, speaker });
  drain();
}
async function drain() {
  if (processing) return;
  processing = true;
  while (queue.length) {
    const c = queue.shift();
    try {
      const audio = await base64(c.blob),
        sent = performance.now();
      const r = await api("audio", {
        session: coach,
        audio,
        speaker: c.speaker,
        chunk_id: crypto.randomUUID(),
      });
      await showAnalysis(r, c.start, sent, c.speaker);
    } catch (e) {
      log("Audio window failed: " + e.message);
      observations.push({ mode: "audio_error", error: e.message });
      err(e);
    }
  }
  processing = false;
  if (!live) {
    $("livestate").textContent = "Stopped";
    $("live").disabled = !config.asr_configured;
    $("language").disabled = false;
  }
}
$("live").onclick = async () => {
  try {
    if (!config.asr_configured)
      throw Error(
        "Set OPENAI_API_KEY in .env and restart to enable live audio.",
      );
    if (!$("audioconsent").checked)
      throw Error("Confirm tester consent before sending audio.");
    if (callRecorder?.state === "recording")
      throw Error("Stop the voice-desk microphone recording first.");
    recognition?.abort();
    speechSynthesis.cancel();
    await coachSession();
    mic = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: false,
        noiseSuppression: false,
        channelCount: 1,
      },
    });
    context = new AudioContext();
    await context.resume();
    const source = context.createMediaStreamSource(mic);
    processor = context.createScriptProcessor(4096, 1, 1);
    gain = context.createGain();
    gain.gain.value = 0;
    source.connect(processor);
    processor.connect(gain);
    gain.connect(context.destination);
    samples = [];
    allAudio = [];
    sampleCount = 0;
    windowStart = performance.now();
    windowSpeaker = $("speaker").value;
    live = true;
    $("language").disabled = true;
    $("live").disabled = true;
    $("stoplive").disabled = false;
    $("livestate").textContent = "Live · 4s windows";
    processor.onaudioprocess = (e) => {
      if (!live) return;
      const c = new Float32Array(e.inputBuffer.getChannelData(0));
      allAudio.push(c);
      if ($("speaker").value !== windowSpeaker) flushWindow();
      samples.push(c);
      sampleCount += c.length;
      if (sampleCount >= context.sampleRate * 4) flushWindow();
      if ((allAudio.length * 4096) / context.sampleRate > 300)
        $("stoplive").click();
    };
  } catch (e) {
    mic?.getTracks().forEach((t) => t.stop());
    err(e);
  }
};
$("stoplive").onclick = async () => {
  if (!live) return;
  live = false;
  flushWindow();
  const rate = context.sampleRate;
  processor.disconnect();
  gain.disconnect();
  mic.getTracks().forEach((t) => t.stop());
  await context.close();
  download(wavBlob(allAudio, rate), "live-call-" + Date.now() + ".wav");
  allAudio = [];
  $("stoplive").disabled = true;
  $("livestate").textContent = processing
    ? "Finishing queued audio"
    : "Stopped";
  if (!processing) {
    $("live").disabled = !config.asr_configured;
    $("language").disabled = false;
  }
};
$("exportmetrics").onclick = () =>
  jsonDownload(
    {
      created_at: new Date().toISOString(),
      provider: config.model,
      observations,
      metrics,
      notes: {
        timing:
          "Monotonic browser capture-start to post-render. Server ASR is provider round trip. Delivery residual includes upload, queue, and browser scheduling.",
        confidence:
          "Audio confidence is not calibrated. Rule certainty is not ASR accuracy.",
        speaker: "Manual per-window attribution; not automatic diarization.",
        llm: "Not used",
        status: metrics.some((x) => x.mode === "live_audio")
          ? "live_audio_observed"
          : "text_only_not_Q4_audio_evidence",
      },
    },
    "insights-evidence-" + Date.now() + ".json",
  );
$("recordcall").onclick = async () => {
  try {
    if (callRecorder?.state === "recording") {
      callRecorder.stop();
      return;
    }
    if (live) throw Error("Stop Live Insights first.");
    if (
      !confirm(
        "Record your microphone locally? Obtain consent from every participant. This does not capture system audio.",
      )
    )
      return;
    callMic = await navigator.mediaDevices.getUserMedia({ audio: true });
    callChunks = [];
    callRecorder = new MediaRecorder(callMic);
    callRecorder.ondataavailable = (e) => {
      if (e.data.size) callChunks.push(e.data);
    };
    callRecorder.onstop = () => {
      download(
        new Blob(callChunks, { type: callRecorder.mimeType }),
        "microphone-" +
          Date.now() +
          (callRecorder.mimeType.includes("mp4") ? ".mp4" : ".webm"),
      );
      callMic.getTracks().forEach((t) => t.stop());
      $("recordcall").textContent = "Record microphone";
      $("recordstatus").textContent =
        "Saved microphone track. Verify both sides using your separate screen recording.";
      $("language").disabled = false;
    };
    callRecorder.start();
    $("language").disabled = true;
    $("recordcall").textContent = "Stop & download";
    $("recordstatus").textContent = "Recording microphone only…";
  } catch (e) {
    err(e);
  }
};
fetch("/api/config")
  .then((r) => r.json())
  .then((c) => {
    config = c;
    $("connection").textContent = "● Local server connected";
    $("live").disabled = !c.asr_configured;
    if (!c.asr_configured)
      log("Live ASR is not configured. Text checks are available.");
  })
  .catch(err);


$("replay").onclick = async () => {
  let replayContext, player;
  try {
    if (live || processing) throw Error("Finish the current audio session first.");
    if (!config.asr_configured) throw Error("Configure local ASR or the provider key first.");
    if (locale() !== "en-PH") throw Error("Choose Philippines English in Voice desk for this English fixture.");
    const manifest = await (await fetch("/demo/stream.json")).json();
    const audio = await (await fetch("/demo/stream.wav")).arrayBuffer();
    replayContext = new AudioContext();
    await replayContext.resume();
    const decoded = await replayContext.decodeAudioData(audio);
    const rate = decoded.sampleRate;
    const pcm = decoded.getChannelData(0);
    coach = null;
    await coachSession();
    activeNudges = []; metrics = []; observations = []; queue = [];
    $("streamlog").replaceChildren(); renderNudges(); renderMetrics();
    live = true; $("language").disabled = true; $("live").disabled = true; $("replay").disabled = true;
    player = replayContext.createBufferSource(); player.buffer = decoded; player.connect(replayContext.destination);
    const t0 = performance.now(); player.start();
    $("livestate").textContent = "Real-time audio replay";
    for (let i = 0; i < manifest.windows.length; i++) {
      const end = (i + 1) * 4000;
      $("replaystatus").textContent = `Playing window ${i+1}/${manifest.windows.length} · session ${coach}`;
      await new Promise(resolve => setTimeout(resolve, Math.max(0, t0 + end - performance.now())));
      const frame = pcm.slice(Math.round(i * 4 * rate), Math.round((i+1) * 4 * rate));
      queue.push({blob:wavBlob([frame], rate),start:t0+i*4000,speaker:manifest.windows[i].speaker});
      drain();
    }
    live = false;
    while (processing) await new Promise(resolve => setTimeout(resolve, 100));
    const evidence = {provider:config.provider, model:config.model, mode:"real_time_synthetic_audio_replay", duration_s:decoded.duration, observations, metrics, fixture:manifest};
    $("replayreport").textContent = JSON.stringify(evidence,null,2);
    await api("measurements",{session:coach,evidence});
    $("replaystatus").textContent = `Replay complete · ${metrics.length} audio windows · session ${coach}`;
  } catch (e) { err(e); }
  finally { live=false; $("replay").disabled=false; $("language").disabled=false; $("live").disabled=!config.asr_configured; if(replayContext) await replayContext.close(); }
};
