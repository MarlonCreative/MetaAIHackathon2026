# CasaOS — Home Stack v0.4

**Home Stack** = the inventory, relationships, operating constraints, and planned upgrades of a home’s essential infrastructure. Separate *installed*, *unknown*, and *proposed* assets. Model interdependencies rather than treating utilities as independent toggles.

## Property
Two houses in the La Libertad / Atami area of El Salvador, with occasional power and water interruptions. There is limited indoor equipment space. No claim of direct sensors or remote access.

## Existing, reported

| Layer | Item | Confirmed detail | Still needed |
|---|---|---|---|
| Electricity | DELSUR utility grid (sole current power source) | Service exists; no generator or solar installed | Meter/plan, outage history, main panel, peak load |
| Water | ATAMI Residential → cistern → **electric distribution pump** → houses | Private residential water supply, onsite storage, and confirmed electric delivery pump | Cistern capacity, refill schedule, electric pump model, running watts, startup surge, plumbing arrangement |
| Connectivity | Cabal internet | Service exists | Access technology, uptime, router power draw, backup power |
| Buildings | Two houses | Main and smaller structure | Per-building circuits, appliances, roof measurements, outdoor secure cabinet |

## Proposed — not installed

- **Solar + battery:** model photovoltaic nameplate kWp, battery kWh, peak solar hours, performance losses, critical vs discretionary loads, inverter and surge constraints. These inputs are hypothetical and adjustable.
- **Generator:** simulate running kW, fuel inventory, burn rate, operating hours and outage time. Generator is **not installed**. Require professional transfer switching, outdoor exhaust management and safe fuel storage.
- **Starlink:** optional connectivity alternative, not installed. Requires independent electricity supply; consider whether Cabal and Starlink share upstream failure risks. No subscription or bandwidth simulation yet.
- **Well:** model potential pump flow (L/h), duration, and energy draw. *Do not count well water as available* unless feasibility, usable quality, and permits are assumed/verified. A well is not a guaranteed answer to supply interruption.

## Scenarios

1. DELSUR grid outage for 24–96 hours.
2. Low cistern during a grid outage.
3. Internet outage when remote monitoring cannot be trusted.
4. Proposed solar/battery backup, with or without a usable well.

## Calculations (simplified)

- Backup electrical energy ≈ usable battery kWh + PV kWp × equivalent peak sun hours × performance factor × days; optional generator kWh ≈ rated kW × min(available fuel / fuel burn rate, daily allowed runtime × days).
- Scenario electricity needed ≈ assumed essential kWh/day × days; if using a well, add pump energy.
- Stored water ≈ cistern volume × fill fraction.
- Potential well water ≈ assumed output L/h × pump hours/day × days. Count only under an explicit usable-water assumption and constrain by available energy.
- Energy and water percentages are **aggregate scenario estimates**, not time-resolved service guarantees.

## Needed from homeowner

Ask for installation facts rather than guessed metrics: cistern liters or dimensions, current water source and pump arrangement, internet provider and router power, utility bill or typical kWh/month, AC ratings and operating schedule, approximate usable roof dimensions, available outdoor equipment location, desired critical loads, and local well feasibility/neighbor observations.

## Safety / ethics

Simulation only. No automatic switching, grid interconnection, well drilling, pump restart, or safety-critical water treatment decisions. Actual design requires a qualified local solar electrician, electrical survey, well driller, local permissions, and water testing.

## Hackathon demonstration

Contrast current stack against solar, generator, solar+generator, and solar+well using the same 48-hour outage; visually show cascading dependencies: the grid powers the pump, the pump transfers water, networking relies on electricity, and a well draws energy even when water is underground. Position Muse Spark as an agent that asks for missing stack details, analyzes constraints, calls read-only simulation tools, and explains trade-offs with provenance. The current stack comparison itself is deterministic and works offline.

## Confirmed dependency (Nov 2, 2026)

The homeowner confirmed that the cistern uses an **electric pump** to supply the houses. With DELSUR as the sole existing power source, an outage may interrupt normal household water delivery **even if the cistern is full**. The simulation must not equate stored liters with accessible pressurized household water. Backup scenarios show only *conditional* access until pump watts, startup surge, transfer method and backup circuit are confirmed. A proposed well would itself need pumping power and water testing.
