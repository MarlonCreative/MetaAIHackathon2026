# CasaOS — agent-centered hackathon pitch

## One sentence

CasaOS puts an AI agent inside a simulated two-house property in El Salvador to test how coordinated decisions about power, water, and connectivity could keep essential services available through a storm.

## Submission summary

At our reference property in coastal El Salvador, losing grid power can also stop the electric cistern pump: stored water does not mean water at the tap. CasaOS turns that local problem into a playable resilience mission. A homeowner can add *virtual* solar, battery, and generator equipment, run a reproducible 72-hour storm, and watch a controller make decisions as conditions change. The simulator accounts for energy, fuel, stored water, pump constraints, and service uptime; the same scenario runs against a fixed-rule baseline for an honest comparison.

The agent is the technical frontier. A Meta model can inspect virtual sensors and equipment dependencies, forecast resources, compare a proposed action with holding current controls over twelve simulated hours, request a simulated control, and inspect the outcome on a later step. Tool requests pass through a deterministic safety gate before they can change simulation state. The model does not invent the physics or directly control real equipment. Its decisions are recorded alongside the baseline so we can measure whether adaptation helps, hurts, or has no effect.

CasaOS shows a path for developers in El Salvador to build agents around problems they know firsthand. The same model-and-tools pattern could eventually support other homes and local infrastructure, once equipment data, local inference, and safe hardware adapters are validated. This prototype is a planning sandbox, not an operational home controller.

## What to demonstrate

1. **Grounded observation:** Show the two-house dependency: DELSUR power → electric pump → household water, plus ATAMI cistern supply and Cabal internet. Label proposed backup equipment as virtual.
2. **Model-selected tools:** In an authenticated Meta run, show the actual `read_sensors`, `inspect_home_stack`, `forecast_resources`, `evaluate_action`, `request_control_action`, or `inspect_outcome` calls the model made. Show the next-hour follow-up after a changed control. Do not imply a tool was used if it is absent from the audit.
3. **Constrained action:** Show the requested control, safety-gate approval or rejection, before/after simulated state, and the next hour's service outcome. A preview alone is not an executed action.
4. **Adaptation:** Show an unexpected storm event or generator fault, the new observation, and any subsequent change in model behavior. If it did not adapt, say so.
5. **Honest measurement:** Compare against fixed rules with the same input hash. Report critical and water uptime, unmet electricity and water, fuel, and safety results, including unfavorable deltas and fallback periods.

## Evidence status as of November 4, 2026

The offline engine, visual twin, fixed-rule baseline, safety gate, three scenarios, and 31 tests are implemented. A bounded, event-triggered Meta Responses run completed all 72 hours with 31 model-selected tool calls and five accepted state changes. On the same scenario input, the agent **matched** the fixed-rule baseline for critical power, water and network uptime, delivered water, and fuel; it did not demonstrate a meaningful performance gain. The simulator and fallback run locally; hosted Meta inference requires connectivity. Local model inference and physical control remain future work.

## Short spoken pitch

“In El Salvador, a power outage can become a water outage even when the cistern is full. CasaOS lets us test that cascade before buying backup equipment. Its agent can observe a virtual home, use tools to investigate and preview options, request safe simulated controls, and respond to the next outcome. We compare its results with fixed rules under the same storm. This is how powerful models can help local developers tackle physical problems they know firsthand—with measurable results and clear limits.”
