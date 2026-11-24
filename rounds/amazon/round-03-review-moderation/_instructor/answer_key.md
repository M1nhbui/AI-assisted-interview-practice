# Answer key: amazon / round-03-review-moderation

Based on reported variant: **Content moderation on reviews** (add and edit review must call the existing bad-content checker, return 403 on a violation, increment and persist the violation count, flag after 3 strikes, keep blocking flagged users, record the violated words).

Weakness bias (from round-01 and round-02 reviews): ORM persistence and stale in-memory objects (round 2's main blocker), tracing a 403 to the permission/auth helper (round 1's stuck point), and a hidden-only README contract check (found 24 min late in round 2). No bug repeats an earlier round's bug.

Coin flip for a broken test-support file: **tails** (none this round).

5 planted bugs: 3 LISTED in TASK.md, 2 UNLISTED. Line numbers refer to files in `pristine.tar.gz`.

Visible tests on pristine: 2 passed, 4 failed. Hidden tests on pristine: 2 passed (regression guards), 4 failed.

| # | Listed? | File:line | Defect shape | Visible tests broken | Hidden tests broken |
|---|---|---|---|---|---|
| 1 | LISTED: "banned words published by editing" | `reviews/views.py:89` | wrong variable: checks the stored body, not the new one | `test_moderation.py::test_edit_with_banned_words_is_blocked` | none directly (guards check clean edits still work) |
| 2 | LISTED: "three violations, not flagged" | `reviews/services.py:29` | stale in-memory object after `QuerySet.update` (missing `refresh_from_db`) | `test_moderation.py::test_third_violation_flags_member` | `test_hidden_flag_threshold_and_status_endpoint` |
| 3 | LISTED: "flagged members can still post" | `reviews/auth.py:16` | wrong field plus off-by-one: blocks on `violation_count > 3` instead of `is_flagged` | `test_reviews.py::test_flagged_member_cannot_post` | `test_hidden_only_the_flag_blocks` |
| 4 | UNLISTED | `reviews/views.py:33` | wrong ordering: oldest first | `test_reviews.py::test_list_reviews_newest_first` | `test_hidden_list_ordering_ties_and_missing_product` |
| 5 | UNLISTED, hidden-only | `moderation/checker.py:9` | case-sensitive matching: regex `[a-z']+` on un-lowercased text | none | `test_hidden_banned_words_are_case_insensitive_whole_words` |

Bugs outside the view: 3 of 5 (services, auth helper, moderation checker).

## 1. Edit checks the old body (`reviews/views.py`, line 89)

Wrong: `banned = find_banned_words(review.body)`. `review` is the row as stored, so the check runs on the text being replaced. A clean review edited to "a scam" passes the check and is saved.

Fix: `banned = find_banned_words(changes["body"])`.

Shallow fix to watch for: checking both the old and new body. Visible tests pass, but an owner can then never edit a review whose old text contains a banned word (not tested, but wrong by README).

## 2. Flag decision uses a stale count (`reviews/services.py`, lines 26-29)

Wrong:
```python
    Member.objects.filter(pk=member.pk).update(
        violation_count=F("violation_count") + 1
    )
    if member.violation_count >= settings.FLAG_AFTER_VIOLATIONS:
```
`QuerySet.update` writes to the database but does not touch the `member` object in memory. On the third violation the in-memory count is still 2, so the member is flagged one violation late (on the 4th).

Fix: `member.refresh_from_db(fields=["violation_count"])` right after the update (or compare `member.violation_count + 1`).

Shallow fix to watch for: changing the threshold comparison to `>= FLAG_AFTER_VIOLATIONS - 1`. It passes but breaks again the moment anything refreshes the object first.

## 3. Blocked check reads the wrong field (`reviews/auth.py`, line 16)

Wrong: `return member.violation_count > settings.FLAG_AFTER_VIOLATIONS`. A member at exactly 3 (flagged) can still post, and a member a moderator flagged by hand (count 0) is never blocked.

Fix: `return member.is_flagged`.

Shallow fix to watch for: `>=`. All visible tests pass, but `test_hidden_only_the_flag_blocks` fails: the README says only `is_flagged` decides (manually flagged member with count 0 must be blocked; unflagged member with count 5 must not be).

## 4. Review list is oldest first (`reviews/views.py`, line 33)

Wrong: `.order_by("created_at", "id")`. README: newest first, ties by `id` highest first.

Fix: `.order_by("-created_at", "-id")`. Fixing only `created_at` fails the hidden tie test.

## 5. Checker misses capitalised words (`moderation/checker.py`, line 9)

Wrong: `return set(WORD_PATTERN.findall(text))` with `WORD_PATTERN = r"[a-z']+"`. Upper-case letters are not matched at all, so "SCAM" yields nothing and "Ripoff" yields "ipoff".

Fix: `WORD_PATTERN.findall(text.lower())`.

No visible test covers it (all visible banned words are lowercase). Finding it requires reading the README content policy ("case-insensitive") against `checker.py`.

## Full fix diff

```diff
--- moderation/checker.py
-    return set(WORD_PATTERN.findall(text))
+    return set(WORD_PATTERN.findall(text.lower()))
--- reviews/auth.py
-    return member.violation_count > settings.FLAG_AFTER_VIOLATIONS
+    return member.is_flagged
--- reviews/services.py
+    member.refresh_from_db(fields=["violation_count"])
     if member.violation_count >= settings.FLAG_AFTER_VIOLATIONS:
--- reviews/views.py
-        reviews = product.reviews.select_related("author").order_by("created_at", "id")
+        reviews = product.reviews.select_related("author").order_by("-created_at", "-id")
-            banned = find_banned_words(review.body)
+            banned = find_banned_words(changes["body"])
```

Verified: with this diff, 6/6 visible and 6/6 hidden pass. Reverting any single fix fails exactly the tests listed in the table. The `>=` shallow fix for bug 3 passes 6/6 visible and fails 1 hidden.

## Hidden tests (`_instructor/hidden_tests/`)

| Test | What it checks (README) | Bugs |
|---|---|---|
| `test_hidden_banned_words_are_case_insensitive_whole_words` | "SCAM", "Ripoff" blocked; words stored lowercase sorted; "scampi", "Spamming" allowed | 5 |
| `test_hidden_owner_edits_and_access_rules` | PATCH 401/404/403 forbidden/400 empty; rating-only and clean body edits persist | none (regression guard) |
| `test_hidden_flag_threshold_and_status_endpoint` | not flagged at 2, flagged at exactly 3; status endpoint lists violations newest first | 2 |
| `test_hidden_only_the_flag_blocks` | manually flagged (count 0) blocked on create, on create with bad rating (order), and on edit; unflagged with count 5 allowed | 3 |
| `test_hidden_list_ordering_ties_and_missing_product` | newest first with `id` tie-break; 404 for missing product | 4 |
| `test_hidden_moderation_status_access` | 401, 403 forbidden, own empty status shape | none (regression guard) |
