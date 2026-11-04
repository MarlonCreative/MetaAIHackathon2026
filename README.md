# CasaOS — autonomous resilience simulation

Two houses in Atami, El Salvador. Confirmed installed services: DELSUR electricity, ATAMI Residential water via cistern and electric pump, and Cabal internet. Solar, battery and generator in this simulation are **virtual proposed upgrades**. Every capacity, weather profile and consumption figure is illustrative, not a measurement of the property.

## Launch

Python 3.9+; standard library only. From this folder:

```sh
python3 server.py
```

Open http://127.0.0.1:8766/digital-twin.html and use **Measured resilience runs** at the top of the sidebar. Select a scenario and Rules baseline, run it, then scrub the hourly timeline. The existing dashboard remains at http://127.0.0.1:8766/ and its original evaluation and Home Stack features are preserved. The manual scene controls remain a separate legacy sandbox; measured results come exclusively from the Python backend. Moving a manual control after replay returns the scene to that sandbox; scrub again to restore backend replay.

The Three.js scene downloads its original library from jsDelivr, so first load requires internet. Python scenarios, CLI benchmarks, baseline and tests run offline. No offline Meta model has been installed or demonstrated.

## Genuine Meta agent

Use a Meta Model API key in your terminal, never in browser code or a committed file:

```sh
export META_API_KEY='your-key'
export META_MODEL='muse-spark-1.3'
python3 server.py
```

`MODEL_API_KEY` is also accepted by the agent for compatibility; the legacy explanation dashboard uses `MODEL_API_KEY` only. The local `.env` file is read automatically when a Meta run starts and is ignored by Git. Set `META_API_KEY=` there and save to configure without a terminal; no server restart is needed after editing the key. Environment variables take precedence. No key is included in this project.

Choose **Meta agent + baseline A/B** in the scene or run:

```sh
python3 benchmark.py --meta
```

This incurs real Meta API usage, potentially hundreds of inference requests across all three scenarios. The server supports one benchmark job at a time. Calls have a 30-second network timeout; each tick has at most eight model turns and sixteen tool calls. A 90-second tick budget is checked between requests; an in-flight request may overrun it by its timeout. Background jobs can take several minutes. Stop the server to cancel a running UI job.

`agent.py` sends observations to Meta. Meta selects function tools, Python executes only allowlisted virtual tools, and matching `tool_call_id` results return to Meta for reassessment. Tools: `read_sensors`, `inspect_home_stack`, `forecast_resources`, `evaluate_action`, `request_control_action`, `inspect_outcome`. Controls change optional load, pump request, generator request and battery reserve. Essential refrigeration/router demand cannot be disabled. Changes persist across ticks. Every new tick supplies prior outcome, current state and newly observed events. Future fault schedules are not exposed to the model or forecasts.

Actions pass a strict gate; pump dry-run requests and generator fault/empty-fuel starts are rejected. The electrical dispatcher additionally inhibits pump operation without startup surge and running energy. This distinction is logged as a permitted pump *request* followed by an outcome showing whether it actually ran. The model cannot edit measurements, add fuel, repair faults or actuate real equipment.

If inference fails or exceeds its budget, that run permanently switches to the same baseline and is labeled `mixed_meta_rules_fallback`; it is not reported as a pure Meta result. A missing key prevents a live job from starting. An available API key is configuration, not evidence of successful model use. A successful no-tool model turn advances the simulation unchanged and is not counted as tool-use evidence.

Protocol references: [Meta chat completions](https://dev.meta.ai/docs/cookbook/quickstart-chat-completions) and [Meta function calling](https://dev.meta.ai/docs/cookbook/tool-function-calling).

## Reproduce and compare

```sh
python3 -m unittest discover -v
python3 benchmark.py
```

Three checked-in scenario files: `scenarios/sunny.json` (24 h), `scenarios/downpour.json` (24 h) and `scenarios/storm72.json` (72 h). All have seed 42; there is currently no stochastic sampling, so the event tape alone determines disturbances. The storm begins with a grid outage and low irradiance, loses the generator at hour 24, increases water demand at hour 32 and clears partially at hour 48. Failure is unknown to the controller until it occurs. Both controllers see identical observations; only the simulator reads future events.

Each comparison constructs fresh identical state from the same scenario and writes matching SHA-256 input fingerprints. The rules baseline sheds optional demand during grid loss, keeps the pump requested when water is available, and uses 30%/80% battery generator hysteresis. It passes through the same action gate and dispatcher as the agent. No alternate scripted “AI” controller exists.

CLI writes metrics, hourly history, policy actions and (live runs) actual model messages/tool results to `reports/*.json`. Live generation can vary even at temperature zero: deterministic scenario replay is guaranteed, deterministic model decisions are not. Keep the audit with any published result. UI jobs are temporary in-memory records (last eight); use the CLI for durable reports.

Measured metrics: critical refrigeration uptime, network uptime (router power plus upstream availability), water demand fulfillment uptime, combined service uptime, delivered/unmet water, total unmet electrical demand (including deliberately shed comfort load), fuel used, rejected control requests and executed safety invariant violations. A rejected request is not an executed violation. Uptime counts only completely served hourly intervals. Pump runs for the fraction of an hour needed to deliver that hour's demand; there is no pressurized household storage or recovery of prior unmet water demand.

## Current results and limitations

`reports/COMPARISON.md` records the actual baseline measurements and unavailable agent column. **No live Meta run has been performed: no API credential was configured. No AI improvement is claimed.** The fake transport in unit tests tests protocol plumbing and event response only; it is not a model and is never used by the UI or benchmarks.

Implemented: hourly solar/weather/grid/water/battery/fuel dynamics; three repeatable disturbances; baseline; tool-loop implementation with policy controls and explicit fallback; asynchronous local API; scene replay, A/B score and tick-specific action traces; automated tests. Original dashboard, Home Stack and manual scene functionality are retained.

Mocked/assumed: provider availability, weather, all sensors, capacities, loads and equipment. Generator runs at bounded rated output when requested and burns `0.18 L/h + 0.24 L/kWh`; excess generation is curtailed. This conservative illustrative curve is not a verified generator datasheet. Grid charging is allowed; battery charge/discharge efficiency is 92% each way, charging/discharging capped at 3 kW; backup bus running capacity 4 kW and surge ceiling 5 kW. Pump surge is a conservative instantaneous source-capacity test. No transient AC, reactive power, transfer timing, battery degradation, pressure model, well, water treatment or weather API exists. Solar requires the virtual inverter/battery system. No installed-hardware prediction is warranted.

Incomplete: credentialed Meta tool-use proof, genuine Meta response to generator failure, completed live A/B and any measured AI gain; local inference; vendored offline Three.js; browser visual verification (browser tool timed out during this session); video recording and public repository publication. No real hardware control adapters exist. The three-minute walkthrough is in `DEMO.md`.
