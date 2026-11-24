# Prompt 3: Grade an attempt

Start Claude Code in the repo root (any session). Replace the path.

```
Grade the attempt at rounds/<company>/<round>/attempts/<attempt-folder>.

1. Run the visible tests in that attempt's repo, then _instructor/run_hidden.sh on the attempt.
2. Read _instructor/answer_key.md, the attempt's process_log.md and test_runs.log, and diff the attempt's repo against pristine.tar.gz.
3. Write review.md in the attempt folder:
   - Each bug or feature: file, what was wrong, the fix, which tests it broke, and whether I fixed it correctly or only made the test pass.
   - Process: which questions to the assistant helped, where I lost time (use timestamps), and whether I used targeted runs and breakpoints or kept rerunning the full suite (count targeted vs full runs in test_runs.log).
   - The 3 most useful changes for the real assessment.
4. Add one row to the attempts table in PRACTICE_LOG.md.
5. If you notice something about the real format worth recording, suggest an edit to companies/<company>.md but do not make it without asking me.
6. Show me review.md.
```
