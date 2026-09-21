# Local verification

- 26 Python unit tests passed.
- 13/13 authored retrieval and abstention cases passed.
- 20/20 authored nudge cases passed.
- Five HTTP checks passed; see `http-smoke.json`.
- JavaScript parsed successfully with `node --check`. All Python source files passed AST parsing.
- Browser UI verified: local server connected; start-call opening rendered; beneficiary answer displayed its exact source citation; opportunity text check displayed a nudge while audio percentiles remained blank.
- Dashboard layout visually inspected in the local browser.

Not verified: microphone ASR, native voices, provider-backed transcription, real audio latency, regional accents, two-sided recordings, production deployment, or evaluator access to links.

A system compile-cache permission issue was avoided by checking Python syntax through AST parsing without writing to the system cache. It did not affect the passing runtime tests.
