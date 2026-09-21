"""Explicit consent and qualification state machine; business answers always come from KB."""

import re, uuid
from .kb import ROOT, redact
import json

MESSAGES = {
    "en-PH": {
        "hello": "Hello, I’m the Bridgecall automated demo assistant for fictional Harbor Life. This is a simulation, not insurance advice or an offer. May I ask a few screening questions? Please say yes or no.",
        "age": "What is your age in years? Please use digits when typing.",
        "resident": "Do you currently live in the Philippines? Please say yes or no.",
        "consent": "May I create a mock adviser callback request? Please say yes or no. No adviser is contacted by this demo.",
        "time": "What local date and time would you prefer for the callback? Include a date and time, for example 25 September at 3 pm.",
        "confirm": "Please confirm: {time}, local time. Create this mock callback request? Say yes or no.",
        "done": "Your mock callback request is saved locally. No real appointment is booked and no adviser has been contacted.",
        "stop": "Understood. I will stop the screening and will not create a callback request.",
        "fallback": "I don’t have verified information for that question. I can record a mock request for adviser assistance.",
        "human": "I can record a mock request for a human adviser. This demo cannot connect you to a real person. May I record the request? Say yes or no.",
        "conflict": "I heard conflicting or invalid details. Please give one age in years so I can confirm it.",
        "fail": "Those details do not meet this fictional screening rule. This is not an insurance decision. You can still request adviser assistance.",
        "repeat": "Please answer yes or no so I don’t assume your consent.",
    },
    "fil-PH": {
        "hello": "Magandang araw po. Ako ang automated demo assistant ng Bridgecall para sa fictional Harbor Life. Simulation lang ito, hindi insurance advice o offer. Maaari po ba akong magtanong para sa paunang screening? Oo o hindi po.",
        "age": "Ilang taon na po kayo? Kung nagta-type, gamitin po ang numero.",
        "resident": "Nakatira po ba kayo ngayon sa Pilipinas? Oo o hindi po.",
        "consent": "Puwede po bang gumawa ng mock adviser callback request? Oo o hindi po. Wala pang totoong adviser na makokontak sa demo.",
        "time": "Anong petsa at oras po ang gusto ninyo para sa callback, oras sa Pilipinas? Halimbawa, 25 Setyembre, alas tres ng hapon.",
        "confirm": "Pakikumpirma po: {time}, oras sa Pilipinas. Gagawa na po ba ng mock callback request? Oo o hindi po.",
        "done": "Naitala na po sa local demo ang mock callback request. Wala pang totoong appointment o adviser na nakontak.",
        "stop": "Sige po, ihihinto ko ang screening. Hindi ako gagawa ng callback request.",
        "fallback": "Wala po akong verified na impormasyon tungkol diyan. Puwede tayong magtala ng mock request para sa tulong ng adviser.",
        "human": "Puwede po akong magtala ng mock request para sa adviser. Hindi pa kayang ikonekta kayo sa totoong tao sa demo. May pahintulot po ba kayo? Oo o hindi po.",
        "conflict": "May magkasalungat o hindi valid na detalye. Isang edad lang po muna para makumpirma ko.",
        "fail": "Hindi pasok ang detalye sa fictional screening rule na ito. Hindi ito insurance decision. Puwede pa ring humingi ng tulong sa adviser.",
        "repeat": "Oo o hindi po muna para hindi ko ipagpalagay ang pahintulot ninyo.",
    },
    "id-ID": {
        "hello": "Selamat pagi atau siang, Bapak/Ibu. Saya asisten demo otomatis Bridgecall untuk Nusantara Finance fiktif. Ini simulasi, bukan penawaran pembiayaan. Boleh saya lanjutkan? Jawab ya atau tidak.",
        "age": "Berapa usia Bapak/Ibu? Gunakan angka jika mengetik.",
        "resident": "Apakah Bapak/Ibu berdomisili di Indonesia? Jawab ya atau tidak.",
        "consent": "Boleh saya mencatat permintaan callback untuk petugas dalam demo? Jawab ya atau tidak. Belum ada petugas yang dihubungi.",
        "time": "Tanggal dan jam berapa Bapak/Ibu ingin ditelepon? Sebutkan juga WIB, WITA, atau WIT.",
        "confirm": "Mohon konfirmasi: {time}. Simpan permintaan callback demo ini? Jawab ya atau tidak.",
        "done": "Permintaan callback demo sudah disimpan secara lokal. Ini belum menjadi jadwal resmi dan belum ada petugas yang dihubungi.",
        "stop": "Baik, saya hentikan percakapan ini dan tidak membuat permintaan callback.",
        "fallback": "Maaf, informasi itu belum terverifikasi di demo ini. Saya bisa mencatat permintaan bantuan petugas.",
        "human": "Saya bisa mencatat permintaan bantuan petugas. Demo ini belum bisa menyambungkan ke petugas langsung. Boleh saya catat? Jawab ya atau tidak.",
        "conflict": "Maaf, detailnya belum jelas. Mohon sebutkan satu usia agar bisa saya konfirmasi.",
        "fail": "Detail ini perlu diperiksa petugas. Demo ini tidak menentukan persetujuan pembiayaan.",
        "repeat": "Mohon jawab ya atau tidak agar saya tidak menganggap Bapak/Ibu sudah setuju.",
    },
}


def yesno(t):
    t = re.sub(r"[^\w\s]", "", t.lower()).strip()
    if t in {
        "yes",
        "yes please",
        "yes i do",
        "yes po",
        "oo",
        "oo po",
        "opo",
        "ya",
        "iya",
        "iya pak",
        "boleh",
        "setuju",
    }:
        return True
    if t in {
        "no",
        "no thanks",
        "no po",
        "hindi",
        "hindi po",
        "tidak",
        "nggak",
        "gak",
        "enggak",
    }:
        return False
    return None


def normalize_age_words(text):
    units = dict(
        zip(
            "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split(),
            range(20),
        )
    )
    tens = {
        "twenty": 20,
        "thirty": 30,
        "forty": 40,
        "fifty": 50,
        "sixty": 60,
        "seventy": 70,
        "eighty": 80,
        "ninety": 90,
    }
    pattern = (
        r"\b(" + "|".join(tens) + r")(?:[ -]+(" + "|".join(list(units)[1:10]) + r"))?\b"
    )
    text = re.sub(pattern, lambda m: str(tens[m[1]] + units.get(m[2], 0)), text.lower())
    return re.sub(r"\b(" + "|".join(units) + r")\b", lambda m: str(units[m[0]]), text)


class Agent:
    def __init__(self, kb, market, language):
        self.kb = kb
        self.market = market
        self.language = language
        self.state = "start"
        self.slots = {}
        self.events = []
        self.action = None
        self.rules = json.loads((ROOT / "data/rules.json").read_text())

    def msg(self, key, **kw):
        return MESSAGES[self.language][key].format(**kw)

    def respond(self, text):
        text = redact(text.strip())
        citation = None
        answer = None
        if not text and self.state == "start":
            self.state = "permission"
            answer = self.msg("hello")
        elif re.search(
            r"\b(stop|unsubscribe|do not call|tama na|berhenti|jangan hubungi)\b",
            text,
            re.I,
        ):
            self.state = "closed"
            answer = self.msg("stop")
        elif self.state == "closed":
            answer = self.msg("stop")
        elif re.search(
            r"\b(human|real person|tao|adviser please|petugas|manusia)\b", text, re.I
        ):
            self.state = "consent"
            self.slots["reason"] = "human_request"
            answer = self.msg("human")
        else:
            yn = yesno(text)
            age_numbers = re.findall(r"\b\d{1,3}\b", normalize_age_words(text))
            if self.state == "permission" and yn is not None:
                if yn:
                    self.state = "age" if self.market == "PH" else "consent"
                    answer = self.msg(self.state)
                else:
                    self.state = "closed"
                    answer = self.msg("stop")
            elif self.state == "age" and age_numbers:
                ages = list(map(int, age_numbers))
                if len(set(ages)) != 1 or not 1 <= ages[0] <= 110:
                    answer = self.msg("conflict")
                else:
                    self.slots["age"] = ages[0]
                    rule = self.rules["PH"]
                    if not rule["minimum_age"] <= ages[0] <= rule["maximum_age"]:
                        self.state = "questions"
                        answer = self.msg("fail")
                    else:
                        self.state = "resident"
                        answer = self.msg("resident")
            elif self.state == "resident" and yn is not None:
                self.slots["resident"] = yn
                self.state = "consent" if yn else "questions"
                answer = self.msg("consent" if yn else "fail")
            elif self.state == "consent" and yn is not None:
                self.slots["callback_consent"] = yn
                self.state = "time" if yn else "closed"
                answer = self.msg("time" if yn else "stop")
            elif (
                self.state == "time"
                and len(text) >= 5
                and (re.search(r"\d|tomorrow|bukas|besok|alas", text, re.I))
            ):
                if self.market == "ID" and not re.search(
                    r"\b(WIB|WITA|WIT)\b", text, re.I
                ):
                    answer = self.msg("time")
                else:
                    self.slots["callback_time"] = text
                    self.state = "confirm"
                    answer = self.msg("confirm", time=text)
            elif self.state == "confirm" and yn is not None:
                if yn:
                    self.action = {
                        "id": str(uuid.uuid4()),
                        "type": "mock_callback",
                        "market": self.market,
                        "language": self.language,
                        "slots": dict(self.slots),
                        "status": "local_only",
                    }
                    self.state = "done"
                    answer = self.msg("done")
                else:
                    self.state = "time"
                    answer = self.msg("time")
            elif self.state == "done" and yn is not None:
                answer = self.msg("done")
            if answer is None:
                hit = self.kb.answer(text, self.market, self.language)
                if hit:
                    answer = hit["content"]
                    citation = {
                        k: hit[k]
                        for k in (
                            "record_id",
                            "source",
                            "version",
                            "content_sha256",
                            "score",
                        )
                    }
                    if self.state in (
                        "permission",
                        "age",
                        "resident",
                        "consent",
                        "time",
                        "confirm",
                    ):
                        answer += " " + (
                            self.msg("repeat")
                            if self.state == "permission"
                            else (
                                self.msg(
                                    "confirm", time=self.slots.get("callback_time", "")
                                )
                                if self.state == "confirm"
                                else self.msg(self.state)
                            )
                        )
                else:
                    answer = (
                        self.msg("repeat")
                        if self.state
                        in ("permission", "resident", "consent", "confirm")
                        and text.lower()
                        in ("maybe", "perhaps", "not sure", "siguro", "mungkin", "hmm")
                        else self.msg("fallback")
                    )
        event = {
            "customer": text,
            "assistant": answer,
            "state": self.state,
            "citation": citation,
            "action": self.action,
        }
        self.events.append(event)
        return event
