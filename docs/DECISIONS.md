# CasaOS engineering decisions

| Decision | Rationale and evidence |
|---|---|
| Preserve the v1 PRD | The only PRD found in the local workspace matched the original public root PRD blob. It was moved unchanged to docs/PRD.md. Compare against the separately named CasaOS-PRD-v1.md if supplied. |
| Keep the existing simulator | The offline scenarios, baseline, safety gate, and measured outcome trace were already working. Local command `python3 -m unittest discover -v` passed 24 tests on November 3, 2026 ET. |
| Use Meta Responses API | The specified contract is POST /v1/responses with bearer MODEL_API_KEY and muse-spark-1.3. [Meta documentation](https://dev.meta.ai/docs/protocols/responses) confirms it. Updated adapter is committed locally but not yet on public main. |
| Bound credit use | The one live verification attempt used a 128 output-token limit, 20-second timeout, and store:false. It returned HTTP 401; no authenticated model response or tool use is claimed. |
| Save safe evidence | The local verification report contains endpoint, status, model, token ceiling, timeout, and HTTP status, never credentials or raw reasoning. |
| Keep simulation separate from physical equipment | The current DELSUR, ATAMI/cistern/pump, and Cabal services are not controlled. Solar, batteries, generators, wells, and backup internet remain proposed or virtual. |
| Do not claim an AI win | Fake transport tests prove interface plumbing only. A live agent run and equal-scenario A/B report remain necessary. |
