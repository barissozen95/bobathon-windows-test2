# aurora-pay - Claude Code project memory

Every change in this repo is bound by the team handbook (single source of truth):

@docs/ENGINEERING-HANDBOOK.md

Fee rules: @docs/FEE-POLICY.md

Service layout (domain / application / infrastructure / api): @docs/ARCHITECTURE.md

- Tests: `.venv/bin/python -m pytest -q`; mission checks: `.venv/bin/python verify/run.py <m0..m8>`.
- Test-only work goes through the `qa-engineer` agent (`claude --agent qa-engineer`, or "use the qa-engineer agent"). It may edit only `tests/`.
- Bob (IBM) equivalents live in `.bob/` (custom_modes.yaml, rules-qa-engineer/, skills/). Keep `.claude/skills/api-test-writing/SKILL.md` identical to `.bob/skills/api-test-writing/SKILL.md`.
