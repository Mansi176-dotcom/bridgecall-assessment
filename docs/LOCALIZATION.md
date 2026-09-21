# Localization, ASR, and voice configuration

These scripts are localized prototypes. No native-speaker review or real regional-accent measurement has been performed. Text simulations cannot establish accent support.

## Configuration by market

| Market | Voice-desk ASR | Live-audio ASR | TTS | Observed quality |
|---|---|---|---|---|
| PH English | Browser SpeechRecognition, `en-PH` | `gpt-4o-mini-transcribe`, `en` | Installed `en-PH`, otherwise an English voice | Not measured |
| PH Filipino/Taglish | Browser SpeechRecognition, `fil-PH` | Same model, `tl` | Installed `fil`/`tl` voice only | Not measured |
| ID Bahasa Indonesia | Browser SpeechRecognition, `id-ID` | Same model, `id` | Installed `id` voice only | Not measured |

The browser provider/model is not exposed through this API. Record browser/version, OS, locale, and voice name in each test report. The provider API model can be changed through `ASR_MODEL`. Taglish recognition is a test requirement, not a claimed guarantee: single-language hints can distort English finance terms. There is no automatic language detection or accent-specific ASR model in this build.

## Philippines: life insurance / bancassurance

| Situation | Localized wording | Adaptation |
|---|---|---|
| Budget objection | “Kung mabigat sa budget ang premium, puwedeng magpa-callback sa adviser…” | Keeps familiar finance words; avoids an unnatural formal translation of every term |
| Permission | “Maaari po ba akong magtanong para sa paunang screening?” | Uses polite `po` and permission before screening |
| Bank referral | “Ang bank referral ay pagpapakilala sa insurance adviser. Insurance ito, hindi bank deposit.” | Addresses the bank/insurance distinction relevant to bancassurance |
| Missed premium | “Kapag na-miss ang premium, maaaring maapektuhan ang coverage…” | Natural code-switching; no invented grace period |
| Human request | “Hindi pa kayang ikonekta kayo sa totoong tao sa demo…” | Keeps the fallback in the selected customer's language and states the actual limitation |

Required terminology is in approved records: **premium, policy, beneficiary, rider, lapse, coverage, bank referral**. The agent does not invent a price. When testing display/reading of a sample amount, label it as a test fixture: `₱1,500` → “one thousand five hundred pesos” / “isang libo at limang daang piso.” Amount rendering is not a built-in normalization feature. Dates are repeated as customer-provided local text rather than interpreted from ambiguous `09/10` strings.

## Indonesia: consumer finance

| Situation | Localized wording | Adaptation |
|---|---|---|
| Payment difficulty | “Saya paham, Bapak/Ibu sedang kesulitan membayar…” | Respectful support tone instead of a threat or collection demand |
| Colloquial input | “Saya belum gajian, nggak bisa bayar cicilan.” | `belum gajian`, `nggak`, and `cicilan` vocabulary is recognized in retrieval/rules |
| Finance English | “Tenor… sedangkan DP adalah uang muka.” | Explains familiar loanwords instead of replacing them mechanically |
| Callback time | “Sebutkan juga WIB, WITA, atau WIT.” | Explicitly asks for the Indonesian timezone |
| Unknown charge | “Demo ini tidak memiliki tarif denda terverifikasi…” | Refuses to invent a fee and offers a local-language support path |

Required terminology is represented: **cicilan, tenor, denda, DP, jatuh tempo, angsuran, pembiayaan**. The bot uses respectful Bahasa Indonesia even when the customer speaks colloquially. It does not suddenly switch to English. `Rp1.250.000` should be read as “satu juta dua ratus lima puluh ribu rupiah” in an amount-reading test; no actual installment amount is asserted by this demo.

## Regional-accent test — required, still pending

Recruit a consenting Indonesian speaker with a self-described accent outside Jakarta, for example a Javanese-accented Bahasa Indonesia speaker. Ask them to use their natural speech. Do not imitate an accent or label standard TTS as a regional-speaker result.

Suggested prompts (the speaker may rephrase naturally):

1. “Pak, cicilan saya jatuh tempo tanggal dua puluh lima, tapi saya belum gajian.”
2. “Kalau DP-nya segitu, tenornya bisa berapa bulan?”
3. “Bisa ditelepon besok jam sepuluh WIB? Saya mau bicara dengan petugas.”

Run the same prompts with a standard Bahasa speaker for a narrow comparison. Record speaker-reported region/accent, language/register, ASR provider/model, exact human reference, recognized transcript, critical number/term errors, fallback behavior, and a native review of politeness/naturalness. Avoid collecting names or location finer than needed for the voluntary test description.

## ASR report template

| Field | Fill from the recording |
|---|---|
| Test ID / recording link | Pending |
| Provider/model or browser/OS | Pending |
| Spoken language / code-switch examples | Pending |
| Reference transcript / ASR transcript | Pending |
| WER / critical number and finance-term errors | Pending |
| Regional accent / speaker self-description | Pending |
| Quality summary / concrete errors | Pending |
| TTS voice name, locale, missing-voice compromise | Pending |
| Native reviewer observations | Pending |

Use `python3 -m scripts.wer reference.txt hypothesis.txt` for basic word error rate. Keep normalization choices consistent. WER can exceed 100% with many insertions and does not measure whether a wrong number caused a bad business outcome. Report term and number errors separately. If a native voice is unavailable, document that as an unmet voice-quality requirement and capture a text-only fallback; do not claim a native TTS result.
