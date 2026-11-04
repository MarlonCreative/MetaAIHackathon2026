# Reproducible comparison

Baseline measurements from `python3 benchmark.py`. Capacities and weather are illustrative.

| Scenario | Critical uptime | Water uptime | Water delivered | Unmet water | Unmet energy | Fuel | Safety violations | Meta |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| sunny | 24/24 h | 24/24 h | 960 L | 0 L | 0.00 kWh | 0.00 L | 0 | Not run |
| downpour | 24/24 h | 24/24 h | 960 L | 0 L | 25.00 kWh | 0.00 L | 0 | Not run |
| storm72 | 63/72 h | 46/72 h | 2700 L | 1780 L | 183.78 kWh | 1.80 L | 0 | Not run |

Meta results and A/B deltas are absent because no API key was configured. No model performance gain can be inferred. Fake transport tests do not constitute Meta evidence. The 72-hour demand increase and absence of municipal inflow exhaust the cistern, independently of power. Both controllers receive identical initial conditions in a live run.

Test result: 23 tests passed, including all 12 original prototype tests. JavaScript module syntax check passed. See TEST_RESULTS.txt for the saved test log.
