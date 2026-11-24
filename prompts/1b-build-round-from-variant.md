# Prompt 1b: Build a round modeled on a reported real variant

Start Claude Code in the repo root. Replace <COMPANY> (currently only amazon has a variants file). Do not read the output while it builds.

```
Build a new practice round for <COMPANY>, modeled on a reported real assessment variant. I will not read your output, so do not summarize what you built.

READ FIRST
- prompts/1-build-round.md. Follow it exactly (setup, ./t, round files, verify, log), except where this prompt overrides it.
- companies/<company>.md (Builder settings).
- companies/<company>-reported-variants.md (candidate reports of real repo tasks).
- PRACTICE_LOG.md "Rounds built" table.
- Every review.md under rounds/<company>/*/attempts/*/ and the PRACTICE_LOG attempts table. Bias this round's defect shapes toward the weaknesses they name, but never reuse a bug from an earlier round.

PICK A VARIANT
- Choose one reported scenario that works in the profile's stack (Django REST Framework) and has not been used in an earlier round. Good fits: password reset with a 30-second code expiry, loan app with balance checks, comment/issue platform with 401/403 rules, review moderation with strike counting, blog POST with X-User-Id, movie watch-list.
- Build a NEW app inspired by it. Do not copy wording from the notes. Name the folder round-NN-<variant-short-name>.

TASK FORMAT (overrides; match the real assessment)
- TASK.md in the repo root, written like the real assessment prompt: a short app description, then a "Reported issues" list of 2 to 4 broken behaviors written as user-facing symptoms (example style: "Users can fund a loan with insufficient balance"). Never name files, functions or causes. End with: "Pass as many tests as possible. Behavior must follow the API contract in README.md."
- README.md must include an API contract per endpoint: method, path, required fields, required headers, success status, and each error status with its exact message. Tests assert on these.
- Bugs: one per listed issue, plus 1 or 2 UNLISTED bugs (not in TASK.md) that a visible or hidden test catches.
- Flip a coin: if heads, also break one test-support file (a conftest fixture or test helper with an undefined name or wrong import) so some tests error before running. Test assertions themselves stay correct. Note the result in the answer key.
- Use defect shapes from the reports: inverted comparison, object saved but never persisted or never linked to its user/parent, missing existence check, missing or wrong status code or message, missing validation, skipped time-window check, off-by-one.
- At least one bug lives outside the view: in a model, serializer, service/helper module or utility.
- About 6 visible tests that assert status codes, messages and database state. Hidden tests per the profile.

ASSISTANT RULES (write into assistant_rules.txt)
- Time limit 60 minutes. Suggested time-box: 5 min orientation, 10 min reproduce, 35 min fix and iterate, 10 min final full run.
- The assistant can only see a file when I name it or paste it in my message (the real one may only see the open file). It may explain concepts and give generic examples, but never narrows a bug to a file, function or line, confirms guesses, or writes or describes a fix, even if I ask.
- It never edits files or runs tests.

ANSWER KEY additions
- Mark each bug as LISTED or UNLISTED, and say which reported variant this round was based on.
- In the PRACTICE_LOG "Rounds built" row, put the variant name in the Domain column.

When finished, reply only: "Ready: rounds/<company>/round-NN-<name>. Run: bash rounds/<company>/round-NN-<name>/start_attempt.sh <name>"
```
