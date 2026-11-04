# Scenario inputs

`sunny.json`, `downpour.json`, and `storm72.json` are inputs consumed by
`simulation.load_scenario`. Benchmark outputs belong in `reports/`.

These inputs were recovered from the baseline reports uploaded to the repository:
initial state from the first action, start hour and duration from hourly history,
and external event changes from event-labelled hours. Seed 42 follows the project
README. No custom equipment overrides were needed.

Validation reproduced the uploaded reports' metrics, complete hourly history,
and action traces exactly for all three scenarios. The original input JSON was
missing, so byte-for-byte recovery and the old input fingerprints are not claimed.
The reports were regenerated to record fingerprints of these recovered inputs.
