# Reproducible comparison

All capacities and weather are illustrative. The fixed-rule baseline is reproducible from `python3 benchmark.py`; the Meta run is one recorded, credentialed sample. Both used the same storm scenario input hash. Model decisions may vary in another run.

| Storm72 outcome | Fixed rules | Meta agent | Agent minus rules |
|---|---:|---:|---:|
| Critical power uptime | 63/72 h | 63/72 h | 0 h |
| Water availability | 46/72 h | 46/72 h | 0 h |
| Network uptime | 63/72 h | 63/72 h | 0 h |
| Delivered water | 2700 L | 2700 L | 0 L |
| Unmet water | 1780 L | 1780 L | 0 L |
| Unmet electricity | 183.7834 kWh | 183.7717 kWh | −0.0117 kWh |
| Generator fuel | 1.80 L | 1.80 L | 0 L |
| Executed safety violations | 0 | 0 | 0 |

The live run completed all 72 hours with **43 Meta requests, 31 model-selected tool calls, five accepted state changes, and no fallback**. The agent responded to battery alerts and injected events, including the generator fault. This demonstrates a working tool loop and safe simulated control. It does **not** establish a meaningful performance improvement over the baseline.

The 72-hour demand increase and absence of water inflow exhaust the cistern independently of power. The model does not see future injected failures. Replay the exact run with **Replay saved Meta run** in the digital twin. The full audit is in [storm72-meta.json](storm72-meta.json); the independently reproducible rules run is in [storm72.json](storm72.json).

Verification: 31 Python tests passed; JavaScript module syntax and local browser baseline replay passed. See [TEST_RESULTS.txt](TEST_RESULTS.txt).
