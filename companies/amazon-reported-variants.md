# Amazon repo task: reported variants (candidate reports)

Source: notes Minh collected, pasted 2026-11-23. Unverified candidate reports, not official. Used by prompts/1b-build-round-from-variant.md.

Requirements
Provided artifacts: a working repo (loan system, password reset, warehouse, rate-limit/blocklist, etc.) with a README, runnable test suite, and an embedded AI assistant.

Bug list in the prompt typically names 2-4 broken behaviors. Common bug-list framings include:

Loan app: user cannot create a loan; user cannot view existing loans; user can fund a loan with insufficient balance.
Password reset: verification code is never generated; verification skips the 30-second expiry window; reset password is not persisted to the user profile.
Full-stack feature add: implement rate limiting and a keyword/user blocklist on top of an existing repo.
Return-system fraud scoring: items get flagged as non-returnable by a risk score over rating, item value, and account age; six numeric thresholds / weighting bugs are seeded across the scoring path and the AI assistant must help locate them.
Web-backend framework debug: candidate picks one of four backend frameworks (Django / Spring Boot / two others), then fixes two seeded bugs in a small CRUD service so the bundled test suite goes green. You choose the framework up front (Java Spring Boot / Python Django / C++ / others) but cannot switch once inside.
Comment / issue platform (Jira-like): create-comment and update-comment do not persist or display; the fix is usually a saved object never written back or never linked to its issue. Follow the README's API contract — return 401/403 with the right message when the user is unauthenticated / editing someone else's comment, and the success status on completion.
Content moderation on reviews: add review and edit review must call an existing bad-content checker, return 403 instead of 201 on a violation, increment the user's violation count and persist it, set isFlagged = true after 3 strikes, keep blocking an already-flagged user, and record the violated words so the count matches the tests.
Movie-DB watch-list: create / delete / update watch lists and add / remove movies; six unit tests cover adding to a missing list, adding a duplicate, removing, and bulk add-then-remove. Bugs are missing status codes, missing existence checks, and movies never saved to the DB.
Movie-recommendation full-stack (Django + React): after a user marks movies as watched and submits ratings, the Recommended For You section stays empty. Fix the authenticated GET /api/ratings/recommendations/user backend path so it returns up to 10 eligible movies: ratings above 5 boost similar genres by 1.2×, ratings of 5 or below favor other genres, watched-but-unrated movies favor similar genres, and returned movies must have an average rating of at least 7.0. The bundled unit tests define the acceptance contract; the embedded AI assistant can only see the file you have selected, not the whole project.
Movie-search service (Spring Boot): partial-title search returns no results because the incoming query term is not normalized to lowercase while stored titles are lowercase.
Return-policy engine in C++: a larger codebase with a rule engine plus a JSON parser; several seeded bugs sit outside the obvious policy logic, so read helper modules and tests before assuming the failing behavior is in the main engine.
Actor / movie notification app: users follow actors, admins add movies and casts, and followers must be notified when a followed actor appears in a newly added movie. The prompt lists broken behaviors; inspect the files involved in each flow and verify every listed behavior through the UI as well as the bundled tests.
Issue-tracker creation API: validate the required request property, generate a new identifier, persist the new issue, and return the status code required by the bundled schema and tests.
Deliverable: pass as many tests as possible inside the 60-minute window. Some bugs (and sometimes broken test fixtures) are intentionally left out of the prompt — extra credit goes to candidates who notice and fix them.

Django + React blogging variant: repair POST /api/posts/. Read fields from request.data; require title, content, and category; generate defaults for optional fields; associate the saved object with the user identified by X-User-Id; return HTTP 201 with the expected JSON structure, including _id and a nested author; ensure the new entry appears under “My Posts.” The acceptance tests are test_create_post_with_expected_response_structure_and_values and test_save_created_post_to_database.

Examples
Common flows:

Loan repo — three issues listed in the prompt; after the listed fixes 5/6 tests pass and the remaining failure is repay loan with insufficient balance (not mentioned in the prompt).
Password reset repo — fix generate verification code with randint, store generated_at, then check now <= generated_at + 30s on verify; a separate tests/url file has undefined variables that must be patched before tests run; persist the new password into the user profile.
Rate limit / blocklist repo — implement throttling middleware and a moderation hook that blocks flagged keywords and blacklisted users.
Django blogging request fields:

{
  "title": "string",
  "content": "string",
  "excerpt": "string",
  "category": "string",
  "tags": ["string"],
  "readTime": 5
}

Request header: X-User-Id: <user_id>.

Notes
The link in the email says it expires in 7 days, but some reports say that some recruiters have confirmed you have one month from delivery to start the OA. Please check with your own recruiter to be safe.

The AI assistant is reliable enough to do the heavy code editing; the scoring signal is whether you drive a clean reproduce → localize → patch → re-test loop, not whether you can solve the bug from memory. In practice the assistant only helps with syntax / lookups (how to construct a response object); it will not write the fix for you and on some harnesses only sees the file you have open.

Tests assert on the API's returned status code and message, not the UI. Fixing the bug only in the frontend will fail — change the handler and service-level files so the contract holds. Passing 4 of 6 tests has still advanced candidates to recruiter reach-out, so partial completion does not end the loop.

Watch the clock — fixes that pass locally still need to clear the test runner in the sandbox, so leave at least 5 minutes for a final test run before submission.

In the Java actor / movie variant, the provided tests do not cover every listed bug. Manually exercise each broken behavior in the UI after the test suite passes.

In the C++ harness, read README.md and run test.sh; failures can involve syntax errors, incorrect logic, or unfinished functions. The assistant may refuse both direct answers and requests to modify files. Reserve time for the required code push after local verification.

Recent repos in the rotation:

Car-rental app (Node backend) — three independent bugs: My Cars lists cars owned by other users, a newly added car never appears, and edits are lost on refresh. Check the ownership filter, the insert path, and whether the update is actually persisted.
Movie search backend (Spring Boot) — search must partial-match on title, stars, or all fields, ignore case, sort by popularity (with secondary keys), and return only published movies. The matching and sorting rules interact, so the logic is denser than a plain CRUD fix.
OOP-style service with six unit tests in a 60-minute slot, where each failing test hides more than one defect. Candidates pass five of six and run out of time on the last; the AI assistant adds little beyond navigation.
Since late September 2026 the NG/intern OA can run as one algorithm problem (~40 minutes) plus this repo-debug section (~60 minutes), followed by Work Simulation and an LP multiple-choice block.

Preparation
Practice the loop end-to-end on a small repo: clone, npm install/pip install, reproduce a known bug, copy the failing test output into Claude/Cursor, ask for the file and line, apply the minimum diff, re-run tests.
Build a short prompt template you can reuse: "Here is the failing test output and the relevant file; identify the bug and propose the smallest patch." Practice typing it fast.
Read every line of the README and the test files before touching code — the test names often spell out behaviors that are not described in the bug list, which is where the extra-credit fixes hide.
Time-box yourself: 5 min orientation, 10 min reproduce, 35 min fix-and-iterate, 10 min final test run + submit.
Recent variants (2026)
The buggy repo is increasingly a web-framework app — Django (Python) backends are now common, and the AI panel can scaffold framework code at a middling-but-useful level. Paste each failing test into the assistant and ask it to localize the bug to a file / function, then a line range; the assistant is instructed not to hand you the fix outright but will narrow it down.
A multi-file C++ harness (e.g. a return-routing engine across parser.cpp / engine.cpp) shows up in the same slot; editing unfamiliar code in a VS Code-style IDE, the syntax-error churn is the time sink, not the logic.
Typical defects stay shallow: an inverted comparison (==  vs !=, < 0 vs <= 0), a missing state update, an off-by-one. Read the diff carefully — the AI's hints plus a close read usually beat blind regeneration. Six failing tests in ~60 minutes is a normal load and time is tight on the first pass.
In the return-policy engine variant, do not tunnel on the business-rule file. The parser and shared helpers may be seeded with bugs too; start from failing tests, trace data entry points, and verify assumptions at module boundaries.
On the NG OA this round is paired with a workplace simulation (an email-style inbox where you pick the most effective reply) and the work-style survey.
A Node.js + Mongoose CRUD service is in the rotation: roughly six failing tests in the 60-minute window, with the seeded bugs sitting in Mongoose model usage rather than route logic. ORM unfamiliarity is the real time sink — spend the first minutes learning the harness's debugging affordances instead of falling into a print-and-rerun loop.