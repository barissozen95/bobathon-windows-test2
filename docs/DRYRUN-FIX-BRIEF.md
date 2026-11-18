# Brief: template fixes after the 18 November test run

Context: the Aurora Pay Bobathon template was tested end to end with Bob on 18 November. Barış's dry run already fixed the M0 semgrep lookup (ported in the previous commit). Fix the remaining issues below in the template itself (participant facing files and verifiers). Do not touch the reference solutions of the missions and do not solve any mission.

Participant facing text is Turkish. Keep the existing tone. No em dash or en dash characters in any text you write.

## Issues to fix

1. setup.sh says "Python 3.10+ gerekli" and accepts 3.10. Python 3.10 is end of life (Barış hit this). Require 3.11 or newer and update the message. Update README.md and KATILIMCI-KILAVUZU.html where 3.10 is mentioned.
2. KATILIMCI-KILAVUZU.html says "Boss" in 21 places. It must be "Bob".
3. M7 verifier (verify/test_m7_bobcoin.py) passes with a hand written fake JSON. Require a real `bob run --format json` result: at least one JSON document with `"type": "result"` and a `stats` object containing a numeric `session_costs`. Keep stream-json support.
4. M5 verifier (verify/test_m5_findings.py) leaves `PWNED.tgz`, `archives/a` and similar files in the repo when it runs against unfixed code, which breaks the M8 clean tree check. Make the injection probes run in a temporary directory or clean up everything they create, whether the check passes or fails. Add `PWNED*` to .gitignore as a safety net.
5. Bob reads `verify/` on its own (in M1 plan mode it built the plan from verify/test_m1_limits.py). Add a short rule to KATILIMCI-KILAVUZU.html and README.md: do not point Bob at verify/, read the FAIL line yourself and steer Bob with the PRD sentence. Do not add verify/ to .bobignore (it would break M6).
6. M2 makes M4 empty: when asked to fix INCIDENT-2041, Bob also fixed all four M4 hidden bugs and wrote 29 tests, so M4 passed 12/12 without being done. In missions/M2-uretim-hatasi.md state clearly that the scope is only the four complaints, no other behavior change and no new tests. Add a matching note for facilitators to the README section for facilitators if one exists, otherwise to missions/M4-kapsamli-test.md as a short "Not".
7. Bob's file tools cannot write ignore files. In M6 Bob asked the user to create .bobignore. Say in missions/M6-bob-guvenlik-farklari.md that the participant creates .bobignore by hand.
8. `--max-cost` does not stop a running turn: with `--max-cost 0.05` a run cost 0.094 and still reported success. Add this as a Keşif noktası in missions/M7-bobcoin-analytics.md.
9. scripts/scan.sh reports 13 findings and none for A5 (vulnerable dependencies in deploy/worker/requirements.txt). Say in missions/M5-bob-findings.md that A5 is not covered by the Semgrep scan and must be checked by reading the requirement versions (verify still checks it).
10. The IDE creates `.vscode/` in the repo and plan mode left `limits-service-plan.md` in the repo root, both make the M8 clean tree check fail. Add `.vscode/` to .gitignore and mention in missions/M8-github-teslim.md that plan files Bob writes should be committed or deleted.

## Done when

- `./verify/run.sh m0` still passes on this branch.
- A fake `reports/bob-run.json` like `{"result":"x","note":"..."}` fails M7; a real `bob run --format json` output passes the JSON check.
- Running `./verify/run.sh m5` on the unfixed code leaves `git status` without PWNED or archives files.
- `grep -c Boss KATILIMCI-KILAVUZU.html` is 0.
- Report what you changed per item, and anything you could not do.
