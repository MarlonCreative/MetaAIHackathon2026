# CasaOS — personal superintelligence for your home

**A home should tell you where it is vulnerable before the lights go out or the taps stop running.**

CasaOS is a homeowner-directed AI agent concept for more reliable electricity, water, and connectivity. It starts with a real problem at my home in Atami, El Salvador: a grid outage can also stop the electric cistern pump, so stored water may no longer reach the house. CasaOS turns that dependency into an interactive digital twin where a homeowner can explore storms, test virtual backup choices, and see what a Meta AI agent actually does.

This is an early step toward **personal superintelligence for the home**: an agent that understands your home's systems, learns your priorities, warns you about likely weak points, and helps you act before a malfunction becomes a household emergency. [Meta's personal superintelligence vision](https://about.fb.com/news/2026/08/the-future-is-for-everyone/) emphasizes agents that work toward a person's own goals. The [Meta Global AI Developer Hackathon](https://dev.meta.ai/events/global-hackathon) asks builders to solve problems they know firsthand and use Meta's models to understand and control physical systems. CasaOS applies that direction to a homeowner's daily essentials.

Home maintenance is often reactive: a homeowner discovers a failing pump, depleted battery, or fragile internet link only after service stops. With trustworthy sensor history, an agent could notice unusual pump cycling, falling well pressure, reduced solar output, or a battery that no longer holds charge; estimate where failure risk is rising; and recommend maintenance or changes in usage. Where a safe hardware interface exists and the homeowner authorizes it, future versions could also request a switch between grid, solar, battery, and generator power. The goal is a home that helps its owner prepare, not a system that takes control away.

The reference Home Stack has DELSUR electricity, ATAMI Residential water through a cistern and electric pump, and Cabal internet. Solar, battery/inverter, generator, a private well, and backup connectivity are **proposed or simulated**, not installed. Current capacities, loads, weather, and outcomes are illustrative rather than measured home data.

[Agent-centered pitch](docs/PITCH.md) · [Product requirements](docs/PRD.md) · [Demo walkthrough](docs/DEMO.md) · [Submission checklist](docs/SUBMISSION.md) · [Decisions](docs/DECISIONS.md)

## Why an agent

An agent can connect observations to decisions. In the working prototype, **Meta Muse Spark 1.3** selects tools to inspect the simulated home, forecast resources, preview an option, request a virtual control, and inspect the next outcome. A deterministic safety gate checks every request before the simulated state can change. The report records actual model tool calls and compares service results with fixed rules under the same inputs. A complete live Meta tool loop is recorded in [the storm report](reports/storm72-meta.json); the agent matched the baseline's service uptime in that run and did not demonstrate a meaningful gain.

### Working today and what comes next

| Working prototype | Future direction, subject to real sensors and validation |
|---|---|
| Visual twin of a two-house property; simulated rain, grid outages, cistern, pump, solar, battery, and generator. | Connect grid, pump, cistern, well, solar, battery, fuel, and network sensors to a homeowner-owned Home Stack. |
| Meta model tool calls, virtual decisions, safety checks, and an hour-by-hour audit. | Learn normal behavior from sensor history and flag changes that may indicate a maintenance need or rising outage risk. |
| Scenario forecasts and a measured comparison against fixed rules. | Explain likely vulnerabilities, recommend upkeep and usage changes, and compare backup investments before money is spent. |
| No physical equipment control. | With explicit homeowner permission and tested hardware interfaces, request guarded switches among available power sources and verify the outcome. |

The prototype does **not** predict real equipment failures, read live household sensors, draw water from a well, or switch physical power sources. Those capabilities require verified data, device integrations, safety design, and homeowner control.

## Run locally

Python 3.9+ and the standard library are sufficient for the simulation and tests.

```sh
python3 -m unittest discover -v
python3 benchmark.py
python3 server.py
```

Open `http://127.0.0.1:8766/digital-twin.html` for the homeowner Storm Planner. Choose **Explore the storm demo** to replay the saved Meta Muse Spark 1.3 run without new API calls; use **Play the story**, the hourly slider, or the **Jump to a key moment** buttons to watch weather, essential services, and agent actions change. The result panel translates the run into a homeowner takeaway and shows the model's actual tool and control counts. **Try a different plan** runs fixed rules locally or a new Meta agent comparison using credits. Virtual equipment settings and the manual house controls are available in expandable sections. `http://127.0.0.1:8766/` retains the earlier Home Stack explanation dashboard. The Three.js scene loads a library from jsDelivr, so its first browser load needs internet; Python simulation, baseline, and tests run offline.

`scenarios/sunny.json` and `scenarios/downpour.json` run 24 hours; `scenarios/storm72.json` runs 72 hours. The storm injects outage, cloud cover, a generator fault, and increased water demand. The baseline and agent start from identical scenario inputs. The fixed seed is recorded; current state transitions are deterministic and do not sample randomness. `python3 benchmark.py --scenario storm72` writes the reproducible baseline to `reports/storm72.json`; `python3 benchmark.py --meta --scenario storm72` writes a separate live report to `reports/storm72-meta.json`.

## Meta integration and credit limit

Set `MODEL_API_KEY` only in the ignored local `.env` file. Start from `.env.example`; do not paste the key into chat, shell command arguments, screenshots, or committed files. `META_MODEL` defaults to `muse-spark-1.3`.

```sh
python3 -m casaos.meta_verify
python3 benchmark.py --meta --scenario storm72
```

The first command makes **one** `POST /v1/responses` call, with a 20-second timeout, 128 output-token limit and `store: false`; it writes only response ID, status, token counts, and other safe metadata to `reports/meta_live_verification.json`. Run it intentionally because it consumes credits. The second command is a bounded agent run: **at most 80 requests total** for the selected scenario, each with a 30-second timeout, 2048 output-token limit and `store: false`. The agent decides at the start, after a changed virtual control, when battery or service alerts appear, and when a new event arrives; its controls persist between decisions. When the cap or an inference error occurs, the remaining run uses the same fixed rules and is labeled `mixed_meta_rules_fallback`; it is not a pure Meta result. The UI's Meta option uses the same cap.

The agent exposes six virtual tools: sensor and Home Stack reads, resource forecast, action preview, policy-gated control request, and outcome inspection. Every requested control is schema and safety checked before it can affect simulation state. It cannot actuate physical equipment. The audit records simulated observations, requested actions, policy decisions, state changes, response IDs and token counts. Encrypted model reasoning stays in memory for tool-loop replay and is not saved. A mock transport in tests verifies protocol plumbing; it is not evidence of live Meta behavior.

## Measured baseline

Results from `python3 benchmark.py` using illustrative inputs:

| Scenario | Critical uptime | Water uptime | Delivered water | Unmet water | Unmet electricity | Fuel used | Executed safety violations |
|---|---:|---:|---:|---:|---:|---:|---:|
| sunny | 24/24 h | 24/24 h | 960 L | 0 L | 0.00 kWh | 0.00 L | 0 |
| downpour | 24/24 h | 24/24 h | 960 L | 0 L | 25.00 kWh | 0.00 L | 0 |
| storm72 | 63/72 h | 46/72 h | 2700 L | 1780 L | 183.78 kWh | 1.80 L | 0 |

The [recorded live Meta run](reports/storm72-meta.json) completed all 72 hours with the same scenario input hash as the baseline: 43 model requests, 31 model-selected tool calls, five accepted state changes, and no fallback. Critical uptime, water uptime, delivered water, and fuel matched the baseline. Unmet electricity was 0.0117 kWh lower, a negligible difference under illustrative assumptions. See the [comparison report](reports/COMPARISON.md).

## Status

| State | Work |
|---|---|
| Completed | Offline scenarios and fixed-rule baseline; safety gate; simulated outcome metrics and decision trace; complete live Meta tool loop and equal-input A/B report; 31 passing automated tests; v1 PRD imported to `docs/PRD.md`. |
| Completed | Public GitHub source, recorded Meta evidence, and homeowner demo assets synchronized. |
| In Progress | Demo video and platform submission evidence. |
| Blocked | Final submission until video and platform confirmation exist. |
| Not Started | Local open-weight inference and real-hardware adapters; both remain outside this MVP. |

## Limits

The electrical and water models are planning approximations. Pump surge is a capacity check, not transient electrical simulation. No measured pump rating, weather series, load survey, fuel curve, or water pressure model has been verified for the property. Water stored in the cistern can remain unavailable when the pump lacks compatible power. No hardware control API exists. See the PRD for acceptance criteria and future work.
