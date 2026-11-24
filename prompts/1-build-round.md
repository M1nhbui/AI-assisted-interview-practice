# Prompt 1: Build a round

Start Claude Code in the repo root. Replace <COMPANY>. Do not read the output while it builds.

```
Build a new practice round for <COMPANY>'s AI-assisted coding assessment. I will not read your output, so do not summarize what you built.

READ FIRST
- companies/<company>.md, "Builder settings" section. Follow its stack, minutes, task mix, visible/hidden test counts and assistant rule.
- PRACTICE_LOG.md "Rounds built" table, to avoid reusing a domain.
- Every review.md under rounds/<company>/*/attempts/*/ and the PRACTICE_LOG attempts table. Bias this round's defect shapes toward the weaknesses they name, but never reuse a bug from an earlier round.

SETUP
- Use the next round number under rounds/<company>/. Pick a random new domain (orders, library, bookings, etc.). Create rounds/<company>/round-NN-<domain>/.

REPO (build in a temp folder outside this repo first)
- A small, realistic JSON API in the profile's stack, no frontend or templates. For Django: DRF serializers, views/viewsets and routers, spread across models, serializers, views, urls, and one service/helper module.
- README.md (what the app does, setup and run steps) and ARCHITECTURE.md (how the modules fit and the intended behavior of each endpoint). Docs describe the CORRECT behavior.
- Plant the task mix from the profile. Bugs should be mostly silent logic bugs (wrong filter, wrong ordering, off-by-one, inverted permission check, wrong status code), at most one wiring bug (URL route, serializer field, mismatched parameter name). If the mix includes a missing feature, leave a documented endpoint unimplemented in a realistic way.
- Visible tests written the way a real team would. Tests are correct; only app code is buggy.
- Dependency file and test config.
- An executable script ./t in the repo root that runs the test command with whatever arguments I pass, and appends one line to ../test_runs.log: timestamp, exact arguments, passed/failed counts.
- No hints anywhere: no comments, names, TODOs or docstrings pointing to a bug; no git history.

ROUND FILES in rounds/<company>/round-NN-<domain>/
- pristine.tar.gz: the buggy repo.
- assistant_rules.txt: the profile's assistant rule plus the time limit, in plain words for the assistant session.
- start_attempt.sh <name>: extracts pristine into attempts/<name>-<YYYY-MM-DD>/repo/ (add -2, -3 if that folder exists), copies assistant_rules.txt next to repo/, creates empty test_runs.log and process_log.md, and prints the exact setup commands (venv, install, ./t).
- _instructor/answer_key.md: for each bug or missing feature, give the file, the line, what is wrong, the fix, and which visible and hidden tests it breaks.
- _instructor/hidden_tests/: hidden tests per the profile, based on ARCHITECTURE.md.
- _instructor/run_hidden.sh <attempt-folder>: copies hidden tests into that attempt's repo temporarily, runs them, prints results, removes them.

VERIFY
- In a temp copy: confirm the visible tests fail. Apply your fixes and confirm that both the visible and hidden tests pass. Also run start_attempt.sh once into a temp location to check it works. Delete all temp copies.

LOG
- Add a row to the "Rounds built" table in PRACTICE_LOG.md (company, round, domain, stack, date). No bug info.

When finished, reply only: "Ready: rounds/<company>/round-NN-<domain>. Run: bash rounds/<company>/round-NN-<domain>/start_attempt.sh <name>"
```
