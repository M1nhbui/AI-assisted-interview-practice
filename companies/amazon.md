# Amazon AI-assisted assessment profile

Last checked: 2026-11-23
Confidence: candidate reports (plus Minh's own invite). Amazon's official OA pages do not mention the AI-assisted repo task at all. HackerRank's docs describe the platform features but not Amazon's settings.

Labels: [official-Amazon] amazon.jobs pages, [official-HackerRank] HackerRank docs (platform behavior, not Amazon-specific), [invite] Minh's own OA invite, [candidates] candidate reports / prep-site aggregations, [mine] my practice choice.

## Format
- Platform: HackerRank. [official-Amazon] names HackerRank on the SDE II prep page; the university page links a HackerRank practice test (hr.gs). Repo section on HackerRank: [candidates] (Bugnik).
- Sections and order:
  - [invite] about 100 min coding including an AI-assistant repo question, then about 45 min work simulation, then about 6 min work style survey. Set aside 2.5 hours.
  - [candidates] algorithm problem first (no AI allowed), then the repo task. Once you move to the repo section you cannot go back (Bugnik). One SDE II report (Aug 2026): 100 min for both parts together (FastPrep), which matches the invite.
  - [official-Amazon] university SDE page: coding about 70 min, workstyles 15, work simulation 60, survey 5; it does not mention a repo task. These numbers predate or ignore the repo format; trust the invite.
- Repo task time (minutes): not set separately. [invite] 100 min shared by 1 coding question and the repo question. [candidates] about 60 min on the repo (Bugnik, aicodinginterview). [mine] I plan 60 min.
- Task type: mostly bug fixing. [official-HackerRank] code repository questions can be bug fixing or feature building. [candidates] most reports are several bugs in one small app (movie database service in 7 reports, workflow issue tracker in 2, FastPrep); some report implementing two small features instead (aicodinginterview).
- Stack options: [candidates] Java Spring Boot, Python Django, Node.js / MERN (all three sources agree). Flask in one source, C++ in one report. Chosen when opening the invite; cannot switch after starting (Bugnik).
- Stack I practice in: [mine] Python Django (Django REST Framework). The invite lists no stacks; Django appears in every candidate source.
- Visible tests: about 6 [candidates] (5 reports mention 6 tests, FastPrep; scores like "4/6", "6/6", aicodinginterview). Hidden tests: yes [candidates] (Bugnik, PracHub).
- Grading: [candidates] test results; passing all tests was not required in some reports (one passed 4/6 and still got a phone screen). Weighting between algorithm and repo parts: unknown. [official-HackerRank] code repo questions can be scored by automated tests, custom scoring or manual review; which Amazon uses is unknown.
- Bug style: [candidates] "shallow" bugs such as a missing validation, a missing save, a wrong status code, a wrong route (aicodinginterview, one commenter summarizing ~18 reports). Bug counts reported 3 to 8 per repo (Bugnik); one candidate had 6 bugs in 60 min and fixed 2.

## AI assistant
- Can it read the repo? Unknown for Amazon. [official-HackerRank] Ask mode answers questions about the problem, code or specific files, so likely yes.
- Can it write code in chat? [candidates] yes, suggests or writes code in chat (2 reports, Jun and Aug 2026, FastPrep). But 3+ reports call it limited/restricted; one Nov 2026 report says it gave no hint and was weaker than before; one says it would not reveal the bug. Instructions told one candidate not to ask it to solve the problem (aicodinginterview). [official-HackerRank] the default "Guarded" mode helps with syntax and concepts but "does not generate complete solutions".
- Can it edit files or run tests? [candidates] cannot edit the repo (2 reports). PracHub says it "may" edit code, but cites no report. Running tests: unknown (HackerRank docs never mention it). [official-HackerRank] Agent mode (file edits) exists only in Unguarded mode.
- Is the transcript visible to graders? [official-HackerRank] full transcript is in the Detailed Report, on by default for AI-assisted tests. [candidates] Bugnik says it is visible to the evaluator but does not count in your score. Whether Amazon reviewers read it: unknown.

## Builder settings (read by prompts/1-build-round.md)
- Stack: Django REST Framework, pytest-django
- Minutes: 60
- Task mix: 4-6 planted bugs in a small multi-file JSON API, mostly shallow logic bugs (missing validation, missing save, wrong status code, wrong filter/ordering), at most one wiring bug (wrong route or serializer field). Every 3rd round: 2 small missing documented features + 2 bugs.
- Visible tests: about 6
- Hidden tests: 4-6, at least one catching a bug no visible test catches
- Assistant rule: guarded helper. May read the repo, explain code, answer questions, and suggest short code snippets in chat. Does not edit files, run tests, point out where the bugs are, or write the full fix for a failing test unprompted.
- Warm-up before the round: one timed LeetCode medium, about 40 min, no AI, right before the repo round (matches the 100 min shared block).

## Reported variants
- See companies/amazon-reported-variants.md. Key points: the task prompt lists 2 to 4 broken behaviors, some bugs (and sometimes a broken test fixture) are left unlisted, tests assert API status codes and messages from the README contract, and on some harnesses the assistant only sees the open file.
- Use prompts/1b-build-round-from-variant.md for rounds modeled on these.

## My notes
- Real assessment date / deadline: [invite] Fri Nov 27 2026, 3:26 PM CT. My target: finish before Wed Nov 25 2026, 12:00 PM CT.
- Invite: [invite] SDE OA, Nov 2026, 100 min shared by 1 coding question + the AI-assisted repo question, then about 45 min work simulation, about 6 min work style survey. Invite does not list stack options.
- My time plan: about 40 min algorithm, about 60 min repo.
- What happened in the real one (fill in after):

## Sources
- Official, Amazon: https://www.amazon.jobs/content/en/how-we-hire/university/sde-oa (redirects to atoz.amazon), https://amazon.jobs/content/en/how-we-hire/sde-ii-oa-prep. Neither mentions an AI assistant or repo task.
- Official, HackerRank (platform, not Amazon-specific): https://hackerrank-knowledge-base.help.usepylon.com/articles/1152916770-ai-assisted-tests, https://www.hackerrank.com/release/jan-2026, https://www.hackerrank.com/release/apr-2026
- Candidate reports / prep sites:
  - https://www.fastprep.io/experience/amazon-oa-what-it-tests-2026-part-1-of-5-48yclpnezu (Nov 20 2026, aggregates 30 reports)
  - https://bugnik.com/guides/amazon-oa-code-repository-question (Oct 22 2026)
  - https://aicodinginterview.com/blog/amazon-oa-ai-assisted-coding/ (Nov 1 2026)
  - https://prachub.com/resources/amazon-ai-assisted-coding-oa-guide-2026-repository-bugs-ai-prompts-and-hidden-tests (Aug 13 2026)
  - https://www.calibrd.com/interview-prep/amazon-interview
