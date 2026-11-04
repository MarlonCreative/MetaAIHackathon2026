# Hackathon submission tracker

**Public deadline:** November 4, 2026, 9:00 PM Eastern. **Internal upload and verification target:** 7:00 PM Eastern.

The [official Meta event page](https://dev.meta.ai/events/global-hackathon) confirms the Indie Developer track, the Build for Your World and Push the Frontier themes, and the deadline. The three-minute video is specified in the [PRD](PRD.md); verify the final upload fields in the participant submission portal.

## Status

| State | Item | Evidence / next action |
|---|---|---|
| Completed | Offline simulator, baseline, safety gate, reproducible scenarios | `python3 -m unittest discover -v`: 31 passed; `python3 benchmark.py` writes the baseline reports. |
| Completed | Product requirements imported | `docs/PRD.md` is an unchanged copy of the v1 PRD found at repository root. |
| In Progress | Public source repository | Homeowner UI, Meta run evidence, tests, and documentation are prepared locally; verify the public commit and file URLs before submission. |
| Completed | Bounded Meta Responses integration | A credentialed storm run completed with 43 model requests, 31 model-selected tool calls, five accepted state changes, and no fallback. |
| Completed | Equal-input A/B report | `reports/storm72-meta.json` records the full audit; service uptime and fuel match the fixed-rule baseline. No meaningful AI gain claimed. |
| Not Started | Three-minute demo video | Record after selecting truthful live or baseline-only evidence. Retain video URL and playback check. |
| Not Started | Platform submission | Enter project details, source URL, video URL; save confirmation and timestamp. |

## Evidence rules

- Use `docs/PRD.md` as the requirement source. Compare against `CasaOS-PRD-v1.md` if the separate original is supplied.
- Keep installed DELSUR/ATAMI/Cabal infrastructure separate from simulated solar, battery, generator, well and backup internet.
- Report baseline and agent outcomes for identical scenario input hashes, including negative deltas and fallback runs.
- Do not describe a Meta connection check as a tool-loop demonstration.
- The repository and submission must contain no `.env`, API key, private contact details, or unverified performance claims.

## Submission record

- Source: https://github.com/MarlonCreative/MetaAIHackathon2026
- Demo video: pending
- Submission URL or ID: pending
- Submission confirmation time (ET): pending
