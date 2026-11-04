# CasaOS — Meta Global AI Developer Hackathon execution plan

Date: November 2, 2026. Deadline: November 4, 2026, 9pm ET. Indie Developer / Push the Frontier.

## Pitch
A playable, local-first digital twin of a two-house coastal property in Atami, El Salvador. A Meta-powered agent investigates storm-induced utility failures and takes permitted actions on simulated devices to preserve electricity, water delivery, and connectivity.

## What is real, simulated, or not yet built
- Real: property reference photo; known providers DELSUR (electricity), ATAMI Residential (water), Cabal (internet); cistern with electric pump; two houses on one lot.
- Simulation: weather, power outages, water levels and consumption, hypothetical generator/solar/battery, simplified runtime/physical parameters, animated 3D scene.
- Not built yet: verified equipment-spec ingestion, actual sensor adapters, Meta autonomous tool-use loop, validated engineering forecasts, baseline vs agent benchmark, offline model deployment.

## Architecture
- Three.js: render state-driven 3D isometric environment, camera, weather effects, status.
- Python simulation engine: single authoritative environment state, hourly ticking, equipment constraints, observations, deterministic events.
- Meta Muse Spark 1.3: receives compact state and goal, issues structured tool calls, observes tool results, replans. Use meta Model API with a server-side key; never put secrets in browser.
- Policy gate: only permit simulator actions from an allowlist, validate preconditions, cap turns; all failures become observations.
- Recorder: JSONL event trace, scenario seed, controller type, energy/water outcome metrics.

## Minimum winning interaction
1. Load sunny Atami diorama. Click '72-hour tropical storm challenge'.
2. DELSUR outage; because pump depends on electricity, water service stops despite available stored water.
3. Agent invokes `inspect_home_stack`, `read_sensors`, `forecast_solar`, `simulate_action` and `set_virtual_load` or `start_virtual_generator` rather than simply generating prose.
4. Unexpected event occurs (e.g. generator failure or a cloudy second day). Agent receives new state, revises strategy, and acts.
5. Run identical seeded scenario using fixed-rule controller. Compare essential-service uptime, unmet water demand, fuel use, and policy violations. Report honest values; don't script winning numbers.

## Agent tool contracts (design)
- `inspect_home_stack()`: topology, what is installed vs hypothetical, dependencies and validated/unknown equipment specs.
- `read_sensors()`: timestamped virtual sensor readings plus source (`simulated`), confidence, units.
- `forecast_weather(hours)`: seeded local forecast; ground truth can diverge from forecast.
- `simulate_action(action, parameters)`: counterfactual effects without committing state.
- `set_virtual_load(load, enabled)`: toggles an allowed discretionary load within the simulator.
- `set_virtual_pump_schedule(hours)`: respects water reserves, pump availability, and limits.
- `start_virtual_generator()`: requires installed generator, sufficient fuel, safe start and capacity check.
- `get_score()`: measured running metrics, never provided as made-up figures.

## Judging strategy
**Impact 30%**: grounded real homeowner problem of cascading power-water-internet failures. Quantify hours preserved per hypothetical upgrade.
**Meta use 25%**: real multistep function calling, context-dependent tool choices, recovery from denied/failing tool actions, local Muse Glimmer stretch goal.
**Technical 20%**: reproducible seeded runs, state machine with units, independent safety policy, traces, tests, public repo.
**Demo 25%**: photobased Surf City 3D scene; storm arrives; little utility operators move only on actual tool calls; live A/B result cards.

## Priority timeline
**Tonight (Nov 2):** playable low-poly scene + authoritative tick loop + storm trigger + backup toggles. Get the Meta API key ready.
**Nov 3:** implement actual Meta tool loop and policy gate; seed storm scenario; serialize traces; robust tests.
**Nov 4:** A/B benchmark, visual action cues and polished camera; record truthful 3-minute video; verify public GitHub repo and submit before 9pm ET.

## Deliberate exclusions
- No real electrical switching; no claim that an AI model manages certified emergency hardware.
- No exact street address in public repo or videos.
- No unverified real-equipment brand specifications.
- No model-generated 3D scene in lieu of actual stateful engine.
