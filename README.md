# AI-Assisted Interview Practice

Timed practice for company coding assessments where you work in an existing repo with an AI assistant (fix bugs or build a feature, make tests pass).

## Words used here

- **Company profile**: `companies/<company>.md`. What that company's real assessment looks like (stack, time, task type, what the AI assistant can do). The builder reads it so practice matches the real thing.
- **Round**: one generated practice repo with its own planted bugs. `round-01` is the first repo built for a company, `round-02` is a brand new repo (different domain, different bugs), and so on. Rounds never change once built.
- **Attempt**: one person's timed try at one round. You can attempt the same round many times, and so can a friend. Each attempt gets its own fresh copy, so nothing overwrites anything.

## Layout

```
README.md                  this file
PRACTICE_LOG.md            one row per attempt, all companies
prompts/
  0-company-profile.md     research a new company and write its profile
  1-build-round.md         generate a new round (generic bugs)
  1b-build-round-from-variant.md  generate a round modeled on a reported real variant
  2-assistant.md           the AI assistant during your timed attempt
  3-grade.md               reveal bugs, review process, log the score
companies/
  _template.md
  amazon.md
  amazon-reported-variants.md  candidate reports of real Amazon repo tasks
rounds/<company>/round-NN-<domain>/
  pristine.tar.gz          buggy starting state, never touched
  assistant_rules.txt      how the assistant behaves for this company
  start_attempt.sh         makes a fresh attempt folder
  _instructor/             answer key + hidden tests. DO NOT OPEN before grading
  attempts/<name>-<date>/
    repo/                  your working copy
    test_runs.log          every ./t test run, auto-logged
    process_log.md         your questions to the assistant, timestamped
    review.md              debrief after grading
```

## Workflow

1. **New company?** Run `prompts/0-company-profile.md` in Claude Code from this folder. Check the profile it writes.
2. **Build a round**: start Claude Code in this folder, paste `prompts/1-build-round.md` with the company filled in. Do not read its output while it builds.
3. **Start an attempt**: `bash rounds/<company>/<round>/start_attempt.sh <yourname>`, then follow the setup commands it prints.
4. **Do the round**: open a NEW terminal in the attempt's `repo/` folder, start a FRESH Claude Code session, paste `prompts/2-assistant.md`. Decline any file edits. Run tests only with `./t`.
5. **Grade**: back in this folder (any Claude Code session), paste `prompts/3-grade.md` with the attempt path.

Why two separate sessions: the session that planted the bugs knows the answers and will leak hints. The real assessment's assistant does not know the bugs either.

## Retrying and sharing

- Retry a round: run `start_attempt.sh <name>` again. Your old attempt stays.
- New bugs: build a new round.
- Attempts are not committed (see `.gitignore`): each person's attempts, venvs, logs and reviews stay on their own machine. Rounds, prompts, company profiles and `PRACTICE_LOG.md` are shared.
- Keep the GitHub repo **private**. Every round's `_instructor/` folder holds its answer key and hidden tests.

## For a friend using this repo

1. Clone it, then check you have Python 3.10+ (`python3 --version`) and Claude Code (`claude --version`).
2. Pick a round you have not seen: `bash rounds/amazon/<round>/start_attempt.sh <yourname>` and run the setup commands it prints.
3. **Do not open any `_instructor/` folder until you have finished that round.** That is the only thing that keeps the practice honest.
4. Follow the Workflow section above: fresh Claude Code session with `prompts/2-assistant.md` during the round, `prompts/3-grade.md` after.
5. To add your score to the shared log, add your row to `PRACTICE_LOG.md`, then `git pull --rebase && git push`.
6. Built a new round? Commit the whole round folder (`_instructor/` included) and push, and tell the others not to open its `_instructor/`.
