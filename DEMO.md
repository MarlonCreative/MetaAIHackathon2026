# Three-minute demo walkthrough

**0:00–0:25 — The dependency.** Open the existing twin. “Two houses share an electric cistern pump. A full cistern cannot deliver water if DELSUR fails and there is no compatible backup.” Identify ATAMI water and Cabal internet. State that backup equipment is virtual.

**0:25–0:50 — Controlled experiment.** In Measured resilience runs, choose the 72-hour storm. Explain that both controllers receive the same initial battery, fuel, water and disturbance schedule. Show the JSON scenario. The agent does not see future injected failures.

**0:50–1:35 — Real actions.** With credentials configured, show a *previously completed genuine Meta report* and scrub its tool trace. Point to actual model-selected `read_sensors`, a preview if one occurred, and accepted `request_control_action` records with changed before/after state. Show the subsequent outcome. Do not claim a tool was used if it is absent. A full live run may take much longer than this video.

**1:35–2:10 — Unexpected failure.** Scrub hour 24. Show the generator fault in observations, then the model's actual subsequent tool calls and changed controls, if present. Do not substitute unit-test transport output. If the model failed to adapt or the run fell back to rules, say so and show that label.

**2:10–2:40 — Evidence.** Show measured baseline and Meta uptime, delivered/unmet water, unmet electricity, fuel and safety records. Explain positive and negative deltas without selecting only favorable metrics. Show identical input hashes. Distinguish electrical shortage from deliberate comfort shedding.

**2:40–3:00 — Scope.** “This is a planning sandbox using illustrative equipment assumptions, not real home telemetry or physical actuation. The engine and baseline run offline; hosted Meta decisions need internet.” Show tests and name what remains.

**Current recording status:** live Meta evidence is unavailable without credentials. Until a credentialed run succeeds, demonstrate baseline and explain the integration; explicitly state that autonomous Meta behavior and A/B improvement are not yet demonstrated. Do not use a fabricated agent trace. Video has not been recorded.
