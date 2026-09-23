import json, unittest
from app.kb import KnowledgeBase, ROOT, redact, MainText
from app.agent import Agent
from app.nudges import NudgeEngine


class GroundingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kb = KnowledgeBase()

    def test_every_record_resolves_to_source(self):
        sources = json.loads((ROOT / "data/raw/business.json").read_text())
        for r in self.kb.records:
            idx = int(r["source"].split("#/")[1].split("/")[0])
            self.assertEqual(
                r["content"], redact(sources[idx]["answers"][r["language"]])
            )

    def test_missed_payment_word_forms(self):
        for question in (
            "What happens if I miss a premium?",
            "What happens after missing premiums?",
        ):
            hit = self.kb.answer(question, "PH", "en-PH")
            self.assertIsNotNone(hit)
            self.assertEqual(hit["record_id"], "ph-lapse-en-PH")

    def test_market_and_language_isolation(self):
        for r in self.kb.search("premium", "ID", "id-ID"):
            self.assertEqual(r["market"], "ID")
        for r in self.kb.search("premium", "PH", "fil-PH"):
            self.assertEqual(r["language"], "fil-PH")

    def test_out_of_scope_abstention(self):
        self.assertIsNone(
            self.kb.answer("Does coverage include cancer surgery?", "PH", "en-PH")
        )
        self.assertIsNone(self.kb.answer("What is the weather?", "PH", "en-PH"))

    def test_unreviewed_source_never_answers(self):
        self.assertFalse(any("password" in r["content"] for r in self.kb.records))

    def test_ingestion_failure_duplicate_quarantine(self):
        reports = json.loads(
            (ROOT / "data/processed/ingestion_report.json").read_text()
        )
        for status in ("extraction_failed", "duplicate", "quarantined"):
            self.assertTrue(any(r["status"] == status for r in reports))

    def test_pii_redaction(self):
        text = redact(
            "name: Test Person; email test@example.invalid phone +63 917 000 0000"
        )
        for value in ("Test Person", "test@example.invalid", "917"):
            self.assertNotIn(value, text)

    def test_html_boilerplate(self):
        p = MainText()
        p.feed("<nav>home</nav><main>Useful policy</main><footer>copyright</footer>")
        self.assertEqual(p.parts, ["Useful policy"])


class AgentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kb = KnowledgeBase()

    def setUp(self):
        self.a = Agent(self.kb, "PH", "en-PH")
        self.a.respond("")

    def test_complete_flow_requires_confirmation(self):
        for t in ("yes", "28", "yes", "yes", "25 September at 3 pm"):
            self.a.respond(t)
        self.assertIsNone(self.a.action)
        r = self.a.respond("yes")
        self.assertEqual(r["action"]["status"], "local_only")

    def test_no_assumed_consent(self):
        r = self.a.respond("maybe")
        self.assertEqual(r["state"], "permission")
        self.assertIsNone(r["action"])

    def test_conflicting_age(self):
        self.a.respond("yes")
        r = self.a.respond("I am 22 or 32")
        self.assertEqual(r["state"], "age")
        self.assertNotIn("age", self.a.slots)

    def test_spoken_english_age(self):
        self.a.respond("yes")
        self.assertEqual(
            self.a.respond("I am twenty eight years old")["state"], "resident"
        )
        self.assertEqual(self.a.slots["age"], 28)

    def test_conflicting_spoken_age(self):
        self.a.respond("yes")
        self.assertEqual(self.a.respond("twenty two or thirty two")["state"], "age")

    def test_age_boundary(self):
        for age, expected in [
            (17, "questions"),
            (18, "resident"),
            (60, "resident"),
            (61, "questions"),
        ]:
            a = Agent(self.kb, "PH", "en-PH")
            a.respond("")
            a.respond("yes")
            self.assertEqual(a.respond(str(age))["state"], expected)

    def test_no_resident(self):
        for t in ("yes", "28"):
            self.a.respond(t)
        self.assertEqual(self.a.respond("no")["state"], "questions")

    def test_question_preserves_state_and_has_source(self):
        self.a.respond("yes")
        r = self.a.respond("What is a beneficiary?")
        self.assertEqual(r["state"], "age")
        self.assertTrue(r["citation"])

    def test_human_requires_consent(self):
        r = self.a.respond("I want a human")
        self.assertEqual(r["state"], "consent")
        self.assertIsNone(r["action"])

    def test_stop_is_terminal(self):
        self.a.respond("stop")
        self.assertEqual(self.a.respond("yes")["state"], "closed")

    def test_indonesian_timezone_and_local_fallback(self):
        a = Agent(self.kb, "ID", "id-ID")
        a.respond("")
        a.respond("ya")
        a.respond("ya")
        self.assertEqual(a.respond("besok jam 10")["state"], "time")
        self.assertEqual(a.respond("besok jam 10 WIB")["state"], "confirm")
        self.assertIn("Maaf", a.respond("weather tomorrow")["assistant"])

    def test_spoken_indonesian_timezone(self):
        for zone in (
            "waktu Indonesia Barat",
            "waktu Indonesia Tengah",
            "waktu Indonesia Timur",
        ):
            a = Agent(self.kb, "ID", "id-ID")
            for turn in ("", "ya", "ya"):
                a.respond(turn)
            result = a.respond("Tanggal 25 September jam 10 " + zone)
            self.assertEqual(result["state"], "confirm")
            self.assertIsNone(result["action"])

    def test_ambiguous_asr_is_not_consent(self):
        self.assertEqual(self.a.respond("Oh!")["state"], "permission")
        self.assertIsNone(self.a.action)

    def test_no_duplicate_callback(self):
        for t in ("yes", "28", "yes", "yes", "25 September at 3 pm", "yes"):
            self.a.respond(t)
        first = self.a.action["id"]
        self.a.respond("yes")
        self.assertEqual(first, self.a.action["id"])


class NudgeTests(unittest.TestCase):
    def test_missing_disclosure_before_screening(self):
        self.assertEqual(
            NudgeEngine().process("What is your age?", "agent")["nudges"][0]["rule"],
            "missing_disclosure",
        )

    def test_disclosure_suppresses_reminder(self):
        e = NudgeEngine()
        e.process("This is an automated demo", "agent")
        self.assertFalse(e.process("What is your age?", "agent")["nudges"])

    def test_cooldown_and_expiry(self):
        e = NudgeEngine()
        self.assertTrue(e.process("second vehicle", now=0)["nudges"])
        self.assertFalse(e.process("second vehicle", now=10)["nudges"])
        self.assertTrue(e.process("second vehicle", now=26)["nudges"])

    def test_low_confidence_and_noise_suppression(self):
        for text, conf in [("second vehicle", 0.2), ("[noise] second vehicle", 1)]:
            self.assertFalse(NudgeEngine().process(text, confidence=conf)["nudges"])

    def test_negation_and_reported_claim(self):
        for text in (
            "We do not offer guaranteed approval",
            "The customer said guaranteed approval",
            "No guaranteed returns",
        ):
            self.assertFalse(NudgeEngine().process(text, "agent")["nudges"])

    def test_customer_claim_is_not_agent_violation(self):
        self.assertFalse(
            NudgeEngine().process("guaranteed approval", "customer")["nudges"]
        )

    def test_risk_priority(self):
        self.assertEqual(
            NudgeEngine().process("guaranteed approval", "agent")["nudges"][0][
                "priority"
            ],
            100,
        )


if __name__ == "__main__":
    unittest.main()
