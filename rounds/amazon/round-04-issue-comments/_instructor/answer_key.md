# Answer key: amazon / round-04-issue-comments

Based on reported variant: **Comment / issue platform (Jira-like)**: create and update comment do not persist or display; the fix is a saved object never written back, or a comment not shown for its issue; 401/403 with the right message.

Format: matches Amazon's official HackerRank demo. TASK.md is only the two-line demo statement; the issue list lives in README.md ("Issue" section).

Weakness bias (rounds 1 to 3): "looks fine but nothing was saved" (round 2 and 3 blocker), wrong manager / queryset scope, a README rule that a shallow fix will not satisfy (round 3 had two shallow/partial fixes), 401 vs 403, and a hidden-only README rule.

Coin flip for a broken test-support file: **heads**. `tests/conftest.py` passes a field name the model does not have.

5 planted app bugs (3 LISTED in README Issue section, 2 UNLISTED) + 1 broken fixture. Line numbers refer to files in `pristine.tar.gz`.

Visible tests on pristine: 2 passed, 4 failed (all 4 fail with `TypeError` from the `make_comment` fixture). After fixing only the fixture: 2 passed, 4 failed on real assertions.
Hidden tests on pristine: 2 passed (regression guards), 4 failed.

| # | Listed? | File:line | Defect shape | Visible tests broken | Hidden tests broken |
|---|---|---|---|---|---|
| 0 | UNLISTED (fixture) | `tests/conftest.py:44` | wrong keyword (`text=` instead of `body=`) | 4 of 6 fail with `TypeError: Comment() got unexpected keyword arguments: 'text'` | none (hidden tests use their own fixtures) |
| 1 | LISTED: "edits look like they work, old text comes back" | `tracker/views.py:85` | change never written back: `serializer.save()` missing | `test_edit_own_comment_persists` | `test_hidden_only_the_author_edits`, `test_hidden_edit_response_and_auth_variants` |
| 2 | LISTED: "reporters can rewrite other people's comments" | `tracker/auth.py:14` | permission too broad: reporter allowed to edit | `test_reporter_cannot_edit_others_comment` | `test_hidden_only_the_author_edits` |
| 3 | LISTED: "deleted comments still show up and are counted" | `tracker/selectors.py:13` | wrong manager: `issue.comments` uses the default manager, which includes deleted rows | `test_deleted_comment_hidden_from_list_and_count` | `test_hidden_list_order_and_counts_skip_deleted` |
| 4 | UNLISTED | `tracker/views.py:71` | 401 vs 403: PATCH answers `403 forbidden` for an unauthenticated caller | `test_edit_requires_authentication` | `test_hidden_edit_response_and_auth_variants` |
| 5 | UNLISTED, hidden-only | `tracker/serializers.py:16` | `trim_whitespace=False` turns off DRF's default trimming | none | `test_hidden_body_whitespace_is_trimmed` |

Bugs outside the view: 3 of 5 (auth, selectors, serializers), plus the fixture.

## 0. Broken fixture (`tests/conftest.py`, line 44)

`make_comment` calls `Comment.objects.create(..., text=body, ...)`. The field is `body`. Because the fixture returns a factory, the error shows up inside each test as a failure (not a setup error), with the traceback pointing at conftest.py.

Fix: `body=body`. Watch for: changing the model or the tests' assertions instead.

## 1. Edit never saved (`tracker/views.py`, lines 81-86)

Wrong:
```python
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if not serializer.is_valid():
            return error(...)

        comment.edited = True
        return Response(serializer.data)
```
`is_valid()` only validates. Nothing writes to the database, and `serializer.data` renders the unchanged instance, so the response shows the old body (with `edited: true` from memory).

Fix: replace the last two lines with `serializer.save(edited=True)` and `return Response(serializer.data)`.

Shallow fix to watch for: `comment.body = request.data["body"]; comment.edited = True; comment.save()`. It passes the visible test but skips validation and trimming (the hidden whitespace test then fails on the blank edit).

## 2. Reporter can edit others' comments (`tracker/auth.py`, line 14)

Wrong: `return member.id in (comment.author_id, comment.issue.reporter_id)`.

Fix: `return member.id == comment.author_id`.

Shallow fix to watch for: `member.id == comment.author_id or member.is_admin`. README: admins can delete but not edit; the hidden delete-rules test checks an admin edit gets 403.

## 3. Deleted comments listed and counted (`tracker/selectors.py`, line 13)

Wrong: `return issue.comments.select_related("author").order_by("created_at", "id")`. A reverse relation uses the model's default manager (`Comment.objects`, every row), not `Comment.visible`.

Fix: `Comment.visible.filter(issue=issue).select_related("author").order_by("created_at", "id")` (or add `.filter(is_deleted=False)`). Because `comment_count` reuses this function, one fix repairs both. Fixing only the list (e.g. filtering in the view) leaves the count wrong.

## 4. Unauthenticated edit returns 403 (`tracker/views.py`, line 71)

Wrong: in `CommentDetailView.patch`, `if member is None: return error("forbidden", status.HTTP_403_FORBIDDEN)`. README: every endpoint starts with `401 authentication required`.

Fix: `return unauthenticated()`.

## 5. Body whitespace not trimmed (`tracker/serializers.py`, line 16)

Wrong: `serializers.CharField(max_length=1000, trim_whitespace=False, error_messages=BODY_ERRORS)`. DRF trims by default; this turns it off, so `"   "` is accepted as a body and `"  text  "` is stored padded.

Fix: remove `trim_whitespace=False`. Found only by reading the README Rules section against the serializer.

## Full fix diff

```diff
--- tests/conftest.py
-            text=body,
+            body=body,
--- tracker/views.py
-            return error("forbidden", status.HTTP_403_FORBIDDEN)   # in patch, member is None
+            return unauthenticated()
-        comment.edited = True
-        return Response(serializer.data)
+        serializer.save(edited=True)
+        return Response(serializer.data)
--- tracker/auth.py
-    return member.id in (comment.author_id, comment.issue.reporter_id)
+    return member.id == comment.author_id
--- tracker/selectors.py
-    return issue.comments.select_related("author").order_by("created_at", "id")
+    return Comment.visible.filter(issue=issue).select_related("author").order_by("created_at", "id")
--- tracker/serializers.py
-        max_length=1000, trim_whitespace=False, error_messages=BODY_ERRORS
+        max_length=1000, error_messages=BODY_ERRORS
```

Verified: with this diff, 6/6 visible and 6/6 hidden pass. Reverting any single app fix fails exactly the tests in the table.

## Hidden tests (`_instructor/hidden_tests/`)

| Test | What it checks (README) | Bugs |
|---|---|---|
| `test_hidden_body_whitespace_is_trimmed` | blank body 400 on create and edit; padded body stored trimmed | 5 |
| `test_hidden_delete_rules_and_deleted_is_not_found` | 401; stranger and reporter cannot delete; admin cannot edit but can delete; deleted comment is 404 for delete and edit | none (regression guard) |
| `test_hidden_only_the_author_edits` | reporter blocked on others' comment (unchanged, not edited); reporter's own edit saved | 1, 2 |
| `test_hidden_list_order_and_counts_skip_deleted` | oldest first, ties by lowest id; deleted excluded from list and count; counts per issue | 3 |
| `test_hidden_edit_response_and_auth_variants` | empty, non-numeric, unknown header all 401; 404; edit response and DB both updated | 1, 4 |
| `test_hidden_issue_endpoints_and_closed_rule` | issue 404s, list 401, closed check runs before body validation, closed issue detail | none (regression guard) |
