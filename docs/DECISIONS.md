# Engineering decisions

| Decision | Rationale | Evidence or limit |
|---|---|---|
| Keep the local v1 PRD text intact in `docs/PRD.md` | This is the only PRD file found in the workspace and matches the public repository's root `PRD.md` blob. | The separately named `CasaOS-PRD-v1.md` was not found; compare it when supplied. |
| Preserve the existing simulator and dashboard | The source already implements the P0 physics, safety gate, scenarios, baseline, and trace. | `python3 -m unittest discover -v`: 31 tests passed on November 4, 2026 ET. |
| Use Meta Responses API | The specified provider contract uses `POST /v1/responses`, bearer `MODEL_API_KEY`, and `muse-spark-1.3`. | [Meta Responses API](https://dev.meta.ai/docs/protocols/responses), [tool calling](https://dev.meta.ai/docs/tool-calling). |
| Bound live requests | Concentrate model decisions on initial conditions, the outcome after changed controls, resource alerts, and newly observed disturbances. | Connection check: one request, 128 output tokens, 20 seconds. Agent run: at most 80 requests, 2048 output tokens each, 30 seconds per request; virtual controls persist between decisions, with fixed-rule fallback after inference failure. |
| Save safe audit metadata | Verification should be reproducible without leaking secrets or raw model reasoning. | Verification file stores status, model, endpoint, response ID, token counts, and output types. The live agent trace stores simulated state and policy decisions. |
| Keep simulated equipment distinct | Current physical equipment is not the proposed backup stack. | Home Stack and UI labels; no physical actuator interface. |
| Report the live result without claiming a win | A genuine tool loop is demonstrated, and performance is measured against identical input. | `reports/storm72-meta.json`: 31 model-selected tool calls, five accepted state changes, no fallback; service uptime and fuel tie the baseline. |
