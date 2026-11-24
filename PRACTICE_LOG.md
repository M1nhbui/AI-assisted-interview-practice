# Practice Log

| Date | Person | Company | Round | Visible passed | Hidden passed | Minutes used | Test runs (targeted/full) | Top lesson |
|---|---|---|---|---|---|---|---|---|
| 2026-11-23 | Minh | amazon | round-01-library | 6/6 (0 in-round) | 6/6 (after guided walkthrough) | 37 in-round + ~50 guided | 4/6 | Trace a failing assertion URL -> view -> permission/service yourself; test hunches with breakpoint() |
| 2026-11-23 | Minh | amazon | round-02-password-reset | 5/6 at limit, 6/6 final | 6/6 (validator fixed after time) | 80 (limit 60) | 13/14 | Check DB state, not the response; snapshot before experimental edits; README checklist at minute 45 |
| 2026-11-24 | Minh | amazon | round-03-review-moderation | 6/6 in 59 min | 3/6 | 59 (limit 60) | 23/7 | After a test goes green, re-check the README rule (2 shallow/partial fixes); refresh_from_db after QuerySet.update; 1 REVEAL |
| 2026-11-24 | Minh | amazon | round-04-issue-comments | 6/6 in 49 min | 6/6 (hidden-only bug fixed in time) | 51 (limit 60) | 23/10 | First clean round: 0 REVEALs. When a symptom appears in two places, find the shared function first |

## Rounds built

| Company | Round | Domain | Stack | Built on |
|---|---|---|---|---|
| amazon | round-01 | library | Django REST Framework, pytest-django | 2026-11-23 |
| amazon | round-02 | password reset (reported variant) | Django REST Framework, pytest-django | 2026-11-23 |
| amazon | round-03 | review moderation (reported variant) | Django REST Framework, pytest-django | 2026-11-23 |
| amazon | round-04 | issue comments (reported variant, official demo format) | Django REST Framework, pytest-django | 2026-11-24 |
