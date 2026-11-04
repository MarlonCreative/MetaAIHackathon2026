# CasaOS — Product Requirements Document

**Version:** 1.0  
**Date:** November 2, 2026  
**Status:** Working product requirements / hackathon build plan  
**Primary track:** Meta Global AI Developer Hackathon — Indie Developer, *Build for Your World* / *Push the Frontier*  
**Deadline:** November 4, 2026, 9:00 PM Eastern  
**Product tagline:** *The offline AI operator for homes beyond the smart grid.*

## 1. Executive summary

CasaOS is a **local-first, playable digital twin and autonomous resilience agent** for homes whose essential electricity, water, and connectivity systems are unreliable or interdependent. The owner defines their **Home Stack**—a verifiable inventory of installed utilities, appliances, equipment, dependencies, physical limits, and proposed upgrades. In Simulation Mode, they can install virtual solar panels, batteries, generators, pumps, wells, and backup internet, trigger a disturbance, and watch an AI agent adaptively control simulated infrastructure to maintain essential services.

The defining result is not a prettier dashboard or a more articulate recommendation. **The agent must materially improve measurable outcomes in the same simulated scenario compared with a fixed-rule baseline**, or transparently report when it does not.

The reference property is a two-house residence in Atami / La Libertad, El Salvador. Its **installed stack** includes DELSUR grid electricity (no existing backup), private ATAMI Residential water supplied through a cistern and **electric distribution pump**, and Cabal internet. Proposed—not installed—upgrades include solar plus batteries, a generator, a groundwater well, and Starlink.

This product has two modes:

- **Simulation Mode (hackathon MVP):** Virtual sensors and controllers operate against a time-stepped physics-and-resource model; software actions change simulated outcomes. Hardware spec sheets may parameterize model components with clearly labeled source and confidence.
- **Live Home Mode (post-hackathon):** Adapters may connect read-only sensors, then eligible, professionally installed equipment controls. Safety-rated hardware and deterministic interlocks remain authoritative. Live mode is not part of the current prototype.

## 2. Problem

Residents of infrastructure-constrained homes face cascading failures: grid loss can disable an electrically driven water pump even when a cistern is full; network equipment may also lose power; backup equipment is expensive and hard to size. Most smart-home apps assume continuous grid power and cloud connectivity. Most solar calculators estimate generation, not full-house service survival under a sequence of failures.

**Job to be done:** “Before spending money on solar, storage, or a generator, let me test whether a configuration will actually keep my household essentials running through realistic outages—and let an autonomous controller show me what it would do.”

## 3. Users and stakeholders

- **Primary:** Homeowner managing a rural/semi-rural property remotely, with intermittent utilities and limited infrastructure expertise.
- **Secondary:** Property caretaker, electrician/solar installer, community resilience planner.
- **Post-MVP:** Local service technicians and households with live monitoring systems.

### Initial reference environment (known vs unknown)

| Layer | Confirmed installed | Unknown; do not invent | Proposed only |
|---|---|---|---|
| Buildings | Two houses, main and smaller | Floor areas, appliance schedules, panel/circuit topology | Critical-load subpanel |
| Electricity | DELSUR is sole power supply | Meter data, voltage, outage distribution, load and pump startup surge | PV, inverter, battery, generator |
| Water | ATAMI Residential supplies cistern; electric pump delivers water to homes | Cistern volume/fill; pump model/HP, flow, pressure, backup arrangement | Well with tested water quality and viable yield |
| Internet | Cabal service | Connection type, router draw, local failover capability | Starlink backup |
| Climate | Coastal El Salvador location | Site-specific solar irradiance, shade, wet-season variation | Weather-data import |

**Rule:** Every datum carries provenance (`user-confirmed`, `spec-sheet`, `simulated`, `derived`, `unknown`) and a timestamp where applicable.

## 4. Product principles

1. **Act, don't merely advise:** In simulated mode, the AI chooses and executes allowed actions that change later simulated states.
2. **Local-first:** Simulation engine, policy rules, event log, and dashboard work without internet. A local model is the target for autonomous offline inference, contingent on hardware and runtime benchmarks.
3. **Physics before prose:** Deterministic models compute energy, water, and service availability; the model cannot fabricate sensor readings or declare service restored.
4. **Safe by design:** AI actions pass a hard-coded policy/constraint gate. No direct mains switching, unsafe generator start, or pump energization from LLM text.
5. **Evidence over spectacle:** An A/B comparison uses identical initial conditions, event schedules, and random seeds; report failures and uncertainty.
6. **Progressive fidelity:** Start with clearly marked hypothetical specifications; replace them with verified datasheets and measured telemetry over time.
7. **Bilingual future:** English/Spanish interface and practical explanations are a post-MVP priority.

## 5. Hackathon MVP scope (must ship)

### P0 — Required

**P0.1 Home Stack editor**
- Show installed DELSUR → electric cistern pump → household water; ATAMI Residential → cistern; Cabal → connectivity.
- Place proposed equipment into simulation only: PV, battery + inverter, generator, and essential loads.
- Configure pump run watts, startup surge, water use, cistern capacity, load profiles, solar and generator behavior using default *illustrative* assumptions.
- Separate installed, proposed, unverified, and virtual components.

**P0.2 Time-stepped digital twin**
- Hourly or finer time steps over a 24–72 hour scenario (accelerated playback).
- Conservation accounting: electrical demand vs supply, battery state of charge, generator fuel burn, cistern draw/replenishment, service status.
- Correctly model hour-of-day PV output, nighttime, battery reserves and inverter power ceilings; track unmet demand instead of silently allocating nonexistent energy.
- Recognize that water *stored* is distinct from water *deliverable*: electric pump needs sufficient available power and compatible surge/running capacity.
- Inject at least three events: grid outage, cloudy day, and unexpected water demand or generator failure.
- Fixed seed/event tape for reproducible A/B runs.

**P0.3 Agent with genuine tool loop**
- Meta model selects among tools such as `inspect_home_stack`, `read_sensors`, `forecast_energy`, `forecast_water`, `simulate_candidate_action`, `request_control_action`, `inspect_outcome`.
- At each decision interval, agent may choose permitted actions: shed nonessential simulated load, schedule/unschedule pump, choose generator on/off request, preserve battery reserve, change virtual priority of network/refrigeration.
- Actions affect simulator state only after schema validation and deterministic policy evaluation.
- The agent can observe results and revise decisions on later steps. Visible trace shows model tool calls, policy results, and state changes.
- Explicit fallback when Meta inference is unavailable: fixed-rule controller handles simulation; UI honestly labels that autonomy is unavailable.

**P0.4 Baseline comparison**
- Same Home Stack, starting conditions, event tape and time horizon; compare static threshold controller vs agent.
- Display critical-load uptime, pump/water-delivery availability, network uptime, generator liters consumed, unmet demand, policy violations, and aggregate operating cost assumptions.
- Highlight *actual calculated deltas*, including if agent loses. No hard-coded “AI wins” result.

**P0.5 Demo-quality UX and reproducibility**
- A clear two-house visual map (2D/isometric-inspired SVG or CSS is sufficient), component states and energy/water flow indicators.
- Run/pause/reset and speed controls, disturbance cards, timeline, sensor readouts, and agent decision log.
- Public repository with setup instructions, clearly marked hackathon-built changes, reproducible demo seed, and three-minute video.

### P1 — If time remains

- Datasheet-backed preset for one PV panel, battery/inverter, generator and pump, with source URLs, units, uncertainty, and model limitations.
- Scenario import/export JSON; local SQLite or JSONL log; responsive mobile layout.
- Separate generator “unavailable to start” failure event; optimizer objective presets (minimize fuel vs maximize water access).
- Local open-weight model inference if benchmarked on available hardware.

### Out of scope for hackathon

- Live hardware actuation, electrical installation instructions, operational generator start, well drilling, water purification certification.
- Real utility-provider API integrations unless a supported interface is verified.
- Claims of measured accuracy from a reference house without real instrumentation.
- Full 3D game world, dynamic weather downscaling, real-time AC circuit monitoring, production security hardening.

## 6. Core user journey

1. **Create Home Stack:** Select two houses; review confirmed DELSUR, ATAMI/cistern/electric pump, and Cabal links; choose essential loads.
2. **Plan upgrades:** Virtually install solar, battery, inverter and generator; edit assumed capacities; see equipment compatibility flags.
3. **Select a resilience mission:** “Keep water delivery, refrigeration, and communications available for 72 hours with the least fuel.”
4. **Start identical A/B simulations:** Run baseline controller and CasaOS agent against same outage and weather-event timeline.
5. **Observe autonomous decisions:** Agent reads sensors, plans, calls simulation tools, requests control actions, receives policy approval/rejection, and revisits plan.
6. **Review measured outcome:** Scorecard, event trace, trade-offs and limitations; export simulation report.

## 7. Agent design

**Trigger:** Simulation tick, significant change in sensor value, or injected disturbance. Event monitor initiates work without a fresh user prompt.

**Goal:** Maximize weighted availability of critical services while conserving fuel and respecting equipment limitations. User-set priorities are explicit; safety rules cannot be overridden by agent.

**Tools:**

| Tool | Reads/writes | Contract |
|---|---|---|
| `inspect_home_stack` | Read | Assets, dependency graph, provenance, constraints |
| `read_sensors` | Read | Grid status, load, SOC, fuel, cistern volume, pump availability, network |
| `forecast_resources` | Read/compute | Time-indexed expected energy and water based on simulated weather and loads |
| `evaluate_action` | Compute | Non-mutating what-if for a proposed control action |
| `request_control_action` | Write to simulation only | Typed action; hard gate validates constraints before applying |
| `inspect_outcome` | Read | Delta against last tick, unmet demand and prior actions |

**Control loop:** Observe → choose tool → interpret result → propose action → validate → execute in virtual controller → observe subsequent state → repeat. Save model outputs and executed actions separately. Cap tool calls/time per tick; never assume an action succeeded without simulator acknowledgement.

**Policy constraints (examples):** Do not discharge below configured minimum SOC; do not run loads above inverter/transfer capabilities; reject generator request without remaining fuel or with simulated fault; no pump operation if electrical surge/current or source pressure constraints fail; preserve refrigerator/communications as higher-priority loads than air conditioning; reject unspecified/unknown action types.

**Offline behavior:** Deterministic engine and fallback continue locally. Full autonomous tool planning requires a successfully installed, tested local Meta open-weight model runtime. Hosted Muse API cannot function without connectivity; the PRD does not claim otherwise.

## 8. Simulation specification

**State vector (time-indexed):** `grid_available`, `solar_kw`, `essential_load_kw`, `optional_load_kw`, `battery_soc_kwh`, `generator_on`, `fuel_liters`, `pump_on`, `cistern_liters`, `water_demand_liters`, `delivered_water_liters`, `cabal_powered`, `internet_up`, `weather_factor`, `active_faults`.

**Input models:** Solar production from hour-of-day shape × array kWp × irradiance factor × efficiency; battery charge/discharge with usable capacity and power ceiling; generator rated output and fuel curve (approximate unless datasheet available); pump startup surge and running energy, water throughput and cistern capacity; demand profiles for two houses; router power and upstream internet availability distinct from local supply.

**Important limits:** Model is a planning sandbox, not a validated electrical or hydraulic digital twin. Must handle insufficient capacity explicitly and never claim backup power can operate the pump until power and starting surge assumptions pass. For well simulations, assume verified water availability/quality only when explicitly enabled.

**Comparison validity:** Shared disturbance list, same equipment configuration and initial SOC/fuel/water, deterministic seed, time-synchronized runs. Compare at identical timestamps, not cherry-picked windows.

## 9. Success metrics and acceptance tests

### Functional acceptance

- [ ] Full 72-hour virtual outage runs in accelerated time without external network.
- [ ] Cistern can be full while household water delivery is zero because pump power is absent.
- [ ] Simulated solar generates zero at night; cloud event measurably reduces generation.
- [ ] Battery SOC and generator fuel cannot become negative; violating actions are rejected and logged.
- [ ] Agent completes a mission with **at least three genuine model-selected tool calls** and one validated action affecting subsequent simulation state (with Meta inference actually enabled).
- [ ] Agent receives a new event, inspects changed state, and can change its plan.
- [ ] A/B results are reproducible from a shared event seed and display truthful differences.
- [ ] No real-world hardware controls are exposed in MVP; server-side secrets stay out of UI and repo.
- [ ] README explicitly distinguishes current implemented capabilities from planned features.

### Product success targets (hypotheses, not promised results)

- Demonstrate an explainable, meaningful decision trace within a three-minute video.
- For at least one test seed, evaluate whether adaptive control improves critical-service uptime or fuel efficiency against a competent baseline; if not, document why.
- 100% of executed simulated actions must pass policy validation; 0 unsafe commands should be executed.
- A first-time tester understands why an electrical outage can disable water delivery in under 60 seconds.

## 10. Experience and interface

**Main screen:** Miniature two-house property with component overlays; installed/proposed label on each. Top ribbon: grid / usable power / pump availability / deliverable water / network. Sidebar: upgrade inventory and resilience mission. Bottom: time scrubber, injected events and tool trace. End screen: baseline-versus-agent outcome chart and downloadable decision audit.

**Interaction:** One-click prepared scenario and an editable mode for custom specs. Avoid a blank configuration form on first launch. Show each number with units and provenance; show “unknown” rather than invented precision.

## 11. Technical architecture

```text
Home Stack JSON + Equipment Presets
               |
     Time-stepped simulation engine  <--- deterministic event tape
               |
   virtual sensor and control adapters
          /                 \
 fixed-rule baseline    Meta agent tool loop
          \                 /
        policy / safety validator
               |
    state transition + event log
               |
       local web dashboard
               |
   A/B scorecard + replay + report
```

**Preferred prototype:** Python backend with deterministic simulation, local JSON/SQLite persistence, HTML/CSS/JS dashboard, configurable Meta model backend. Use hosted Muse Spark for accessible hackathon iteration if necessary; use Muse Glimmer locally only if quantized model availability, memory, latency, inference runtime, and tool use are validated on the actual development machine. Do not treat offline open-weight execution as demonstrated merely because the simulation itself runs offline.

**Post-hackathon hardware:** Small local computer with sufficient RAM for chosen quantization; local LAN and optional sensor gateway; UPS for controller/router; separated safety-rated controls for all electrical transfers. Actual hardware selection is contingent on benchmarking and licensed installation advice.

## 12. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Hard to build complete 3D world rapidly | Use performant 2D interactive map first |
| Agent just narrates deterministic rules | Require real tool selection, action execution, feedback and trace |
| Fake AI superiority | Equal-seed A/B, nontrivial baseline, publish negative results |
| Unrealistic energy model | Hour-by-hour accounting, clearly labeled assumptions, source-tagged specs |
| Pump startup constraints overlooked | Explicit surge rating and reject unknown/unverified compatibility |
| Internet failure stalls system | Offline simulator + local fallback; optional tested local model |
| Physical hazards | No live actuation; validated adapters and independent hardware interlocks later |
| Competition originality requirements | Public repo, clear timeline and disclosure of work built during hackathon |

## 13. Hackathon delivery priorities and demo

**Build order:** (1) Time-stepped engine + tests; (2) equipment/state graph and two-house UI; (3) baseline controller; (4) Meta model tool-use loop + state-changing actions; (5) controlled A/B replay + results; (6) polish and video. Do not spend initial build time implementing a full 3D game, external utility APIs, or live hardware.

**3-minute demo storyboard:**

- **0:00–0:25:** “My home in El Salvador has a cistern, but without DELSUR my electric pump stops: water in storage isn't water at the tap.”
- **0:25–0:55:** Show Home Stack map and virtually install PV/battery/generator; explicitly explain these upgrades are not present at the real home.
- **0:55–1:50:** Trigger identical 72-hour disruptions; show agent investigating and executing permitted controls; interrupt with cloudy weather / higher water demand.
- **1:50–2:35:** Show the actual state changes, autonomous revision and baseline comparison scorecard.
- **2:35–3:00:** Position local-first operation and the future live adapter; state that simulator and agent are hackathon-built and physical control is future work.

**Submission checklist:** Public source repository; license/rights-compliant materials; a three-minute accessible demo video; explicit Meta model details and validated proof of use; setup, tests, sample seed, known limitations, and clear attribution of work completed during the hackathon period. Deadline per participant guide: Nov 4, 2026, 9 PM ET.

## 14. Post-hackathon roadmap

**Phase A: Accurate planning tool.** Import electricity bills, pump label photography and verified spec sheets; add photovoltaic irradiation inputs, battery aging, generator runtime curves, uncertainty ranges and sensitivity analysis. Produce installer-ready decision brief, not a substitute for a licensed plan.

**Phase B: Offline-first autonomy.** Benchmark an eligible locally running Meta open-weight model on selected device; local speech/Spanish UX as feasible; operate from on-prem local network with offline logs and fail-safe fallback when model/runtime fails.

**Phase C: Read-only live twin.** Connect supported sensors for meter, cistern level, pump status, inverter, fuel and router uptime; secure authentication, telemetry freshness flags and local buffering. Compare forecasts with observed data.

**Phase D: Supervised live orchestration.** Only professionally installed certified transfer/relay equipment and manufacturer-supported APIs; approval workflows, emergency stop, independent interlocks, monitoring, rollback and security audit. No LLM direct physical control.

**Phase E: Wider resilience ecosystem.** Multi-home use, community infrastructure, well/groundwater feasibility, cost optimization, utility alerts, maintenance scheduling and sharing vetted Home Stack configurations.

## 15. Open questions / evidence needed

1. Is the current cistern pump surface-mounted or submersible? Manufacturer/model plate, running watts or HP, surge and voltage.
2. Cistern capacity, height/pressure arrangement, normal water demand and whether both houses share pump and pipework.
3. DELSUR service voltage/circuit arrangement; major appliance load schedule including four prospective AC units.
4. Router/modem power and Cabal connection technology.
5. Roof dimensions, shading, outdoor battery/inverter location, generator footprint and local climate constraints.
6. Development computer chip, memory, disk, and whether local Muse Glimmer can be benchmarked.
7. Intended end users beyond the reference home and whether a licensed installer would review technical planning outputs.

## 16. Definition of done

A stranger can launch CasaOS, view a truthful two-house Home Stack, install **virtual** backup equipment, run a reproducible 72-hour outage, observe a Meta-powered agent select tools and execute policy-validated simulated actions, and inspect whether those actions preserved more critical services than the same home's fixed-rule baseline. The app works as an offline simulation without cloud inference; any claim of offline **AI autonomy** is made only after a locally hosted model has been demonstrated.

---

**Source of requirements:** Homeowner-confirmed details and hackathon participant-guide text supplied in this conversation. All capacities and performance figures absent from the owner's data are illustrative until explicitly verified.
