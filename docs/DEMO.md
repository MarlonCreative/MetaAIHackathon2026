# Three-minute demo walkthrough

**Opening line:** “In El Salvador, a power outage can become a water outage even while the cistern is full. CasaOS lets an agent test what to do before a household buys backup equipment.” The [agent-centered pitch](PITCH.md) contains submission copy and evidence rules.

**0:00–0:25 — The dependency.** Open the existing twin. “Two houses share an electric cistern pump. A full cistern cannot deliver water if DELSUR fails and there is no compatible backup.” Identify ATAMI water and Cabal internet. State that backup equipment is virtual.

**0:25–0:50 — Controlled experiment.** The Storm Planner opens with a guided homeowner view. Choose **Explore the storm demo**. Explain that Meta AI and fixed rules receive the same initial battery, fuel, water and disturbance schedule. The agent does not see future injected failures.

**0:50–1:35 — Agent at work.** Select **Play the story**, then choose **Hour 8 · Virtual generator** under **Jump to a key moment**. The scene shows rain and the approved virtual control while **At this moment** explains what Meta AI checked, previewed, requested, and observed. Open **Technical decision log** for before/after evidence. The saved run uses no new credits. The agent holds controls between changed-action follow-ups, resource alerts, and new disturbances. Do not claim a tool was used if it is absent.

**1:35–2:10 — Unexpected failure.** Choose **Hour 25 · Generator fault**. Show the fault in observations and the model's actual subsequent tool calls. Describe changed controls only if they appear in the audit. The saved run had no rules fallback.

**2:10–2:40 — Evidence.** Show the three essential-service cards, then open **Compare with fixed rules** for delivered/unmet water, unmet electricity, fuel and safety records. Explain positive and negative deltas without selecting only favorable metrics. Show identical input hashes in the report. Distinguish electrical shortage from deliberate comfort shedding.

**2:40–3:00 — Scope.** “This is a planning sandbox using illustrative equipment assumptions, not real home telemetry or physical actuation. The engine and baseline run offline; hosted Meta decisions need internet.” Show tests and name what remains.

**Current recording status:** a genuine 72-hour Meta run is saved in `reports/storm72-meta.json` and can be replayed in the browser. It matched the baseline on service uptime and fuel; do not claim a meaningful AI gain. Video has not been recorded.
