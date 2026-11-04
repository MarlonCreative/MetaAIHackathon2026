# CasaOS

CasaOS is a local-first resilience planning simulator for homes that are located in rural places or places with unreliable energy and water resources. It models a grid outage cascading to an electric cistern pump and internet equipment. DELSUR electricity, ATAMI Residential water through a cistern and electric pump, and Cabal internet are the **currently installed** services in the reference Home Stack. Solar, battery/inverter, generator, well, and backup connectivity are **proposed or simulated**, not installed. All equipment capacities, loads, weather, and outcomes are illustrative simulations, not home measurements.

[Product requirements](docs/PRD.md) · [Demo walkthrough](docs/DEMO.md) · [Submission checklist](docs/SUBMISSION.md) · [Decisions](docs/DECISIONS.md)

## Run locally

Python 3.9+ and the standard library are sufficient for the simulation and tests.

```sh
python3 -m unittest discover -v
python3 benchmark.py
python3 server.py
```

Open `http://127.0.0.1:8766/digital-twin.html` for the two-house scene and **Measured resilience runs**. Choose a scenario and **Rules baseline**, run it, then scrub the hourly timeline. `http://127.0.0.1:8766/` retains the earlier Home Stack explanation dashboard. The Three.js scene loads a library from jsDelivr, so its first browser load needs internet; Python simulation, baseline, and tests run offline.

`scenarios/sunny.json` and `scenarios/downpour.json` run 24 hours; `scenarios/storm72.json` runs 72 hours. The storm injects outage, cloud cover, a generator fault, and increased water demand. The baseline and agent start from identical scenario inputs. The fixed seed is recorded; current state transitions are deterministic and do not sample randomness. `python3 benchmark.py --scenario storm72` writes the reproducible baseline to `reports/storm72.json`.

## Meta integration and credit limit

Set `MODEL_API_KEY` only in the ignored local `.env` file. Start from `.env.example`; do not paste the key into chat, shell command arguments, screenshots, or committed files. `META_MODEL` defaults to `muse-spark-1.3`.

```sh
python3 -m casaos.meta_verify
python3 benchmark.py --meta --scenario storm72
```

The first command makes **one** `POST /v1/responses` call, with a 20-second timeout, 128 output-token limit and `store: false`; it writes only response ID, status, token counts, and other safe metadata to `reports/meta_live_verification.json`. Run it intentionally because it consumes credits. The second command is a bounded agent run: **at most 16 requests total** for the selected scenario, each with a 20-second timeout, 512 output-token limit and `store: false`. When the cap or an inference error occurs, the remaining run uses the same fixed rules and is labeled `mixed_meta_rules_fallback`; it is not a pure Meta result. The UI's Meta option uses the same cap.

The agent exposes six virtual tools: sensor and Home Stack reads, resource forecast, action preview, policy-gated control request, and outcome inspection. Every requested control is schema and safety checked before it can affect simulation state. It cannot actuate physical equipment. The audit records simulated observations, requested actions, policy decisions, state changes, response IDs and token counts. Encrypted model reasoning stays in memory for tool-loop replay and is not saved. A mock transport in tests verifies protocol plumbing; it is not evidence of live Meta behavior.

## Measured baseline

Results from `python3 benchmark.py` using illustrative inputs:

| Scenario | Critical uptime | Water uptime | Delivered water | Unmet water | Unmet electricity | Fuel used | Executed safety violations |
|---|---:|---:|---:|---:|---:|---:|---:|
| sunny | 24/24 h | 24/24 h | 960 L | 0 L | 0.00 kWh | 0.00 L | 0 |
| downpour | 24/24 h | 24/24 h | 960 L | 0 L | 25.00 kWh | 0.00 L | 0 |
| storm72 | 63/72 h | 46/72 h | 2700 L | 1780 L | 183.78 kWh | 1.80 L | 0 |

The existing report has **no verified live Meta A/B result or AI gain**. A successful connection check only proves one authenticated response; agent tool use and outcome improvement require a separately recorded run. See [comparison report](reports/COMPARISON.md).

## Status

| State | Work |
|---|---|
| Completed | Offline scenarios and fixed-rule baseline; safety gate; simulated outcome metrics and decision trace; 24 passing automated tests; v1 PRD imported to `docs/PRD.md`; bounded Responses API adapter and mock contract test. |
| In Progress | Public GitHub synchronization; demo and submission preparation. |
| Blocked | Live Meta verification returned HTTP 401 on the single bounded attempt. Full tool-loop evidence and A/B claims require a valid local key and successful recorded run; final submission needs video and platform confirmation. |
| Not Started | Local open-weight inference and real-hardware adapters; both remain outside this MVP. |

## Limits

The electrical and water models are planning approximations. Pump surge is a capacity check, not transient electrical simulation. No measured pump rating, weather series, load survey, fuel curve, or water pressure model has been verified for the property. Water stored in the cistern can remain unavailable when the pump lacks compatible power. No hardware control API exists. See the PRD for acceptance criteria and future work.
