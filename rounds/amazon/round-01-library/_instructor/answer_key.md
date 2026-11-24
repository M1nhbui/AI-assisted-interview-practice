# Answer key: amazon / round-01-library

5 planted bugs, no missing feature. Line numbers refer to the files in `pristine.tar.gz`.
Visible tests failing on the pristine repo: 4 of 6. Hidden tests failing on pristine: 5 of 6 (the late-fee test is a regression guard and passes on pristine).

| # | File:line | Kind | Visible tests broken | Hidden tests broken |
|---|---|---|---|---|
| 1 | `library/permissions.py:7-8` | inverted permission check | `test_books.py::test_list_books_sorted_by_title` | `test_hidden_catalog_writes_are_staff_only`, `test_hidden_available_copies_track_open_loans_only` |
| 2 | `library/services.py:21` | wrong filter | `test_loans.py::test_cannot_borrow_when_all_copies_are_out` | `test_hidden_available_copies_track_open_loans_only` |
| 3 | `library/services.py:50` | off-by-one | none (hidden only) | `test_hidden_loan_limit_is_inclusive` |
| 4 | `library/views.py:78` | wrong status code | `test_loans.py::test_borrow_book` | `test_hidden_member_below_limit_can_borrow_and_returned_loans_do_not_count` |
| 5 | `library/views.py:60` | wiring: mismatched query parameter name | `test_loans.py::test_list_loans_for_member` | `test_hidden_loan_list_filters_and_ordering` |

## 1. Inverted permission check (`library/permissions.py`, lines 7-8)

Wrong:
```python
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_staff)
        return bool(request.user and request.user.is_authenticated)
```
The two branches are swapped: reading the catalog needs staff, writing it only needs a login. Any desk user can create, edit or delete books, and non-staff users get 403 on `GET /api/books/`.

Fix:
```python
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return bool(request.user and request.user.is_staff)
```
Shallow fix to watch for: only loosening the read branch (e.g. `return True` for safe methods) makes the visible test pass but leaves writes open to non-staff, and allows anonymous reads. The hidden test checks desk POST/DELETE get 403.

## 2. Available copies counts the wrong loans (`library/services.py`, line 21)

Wrong: `on_loan = book.loans.filter(returned_on__isnull=False).count()` counts *returned* loans as on loan. A book whose only copy is out shows as available; a book whose copies all came back shows as unavailable.

Fix: `on_loan = book.loans.filter(returned_on__isnull=True).count()`

Affects borrowing (`borrow_book`), `available_copies` in book responses, and `?available=true`.

## 3. Loan limit off by one (`library/services.py`, line 50)

Wrong: `if active_loans(member.loans.all()).count() > member.max_loans:` lets a member with `max_loans = 3` take a 4th book. ARCHITECTURE.md: "may hold at most 3 books at once".

Fix: `if active_loans(member.loans.all()).count() >= member.max_loans:`

No visible test covers it. This is the hidden-only bug; finding it requires reading the docs against `services.py`.

## 4. Borrow returns 200 instead of 201 (`library/views.py`, line 78)

Wrong: `return Response(LoanSerializer(loan).data, status=status.HTTP_200_OK)` at the end of `LoanViewSet.create`. ARCHITECTURE.md: success returns `201`.

Fix: `status=status.HTTP_201_CREATED`. (Line 87, in `return_book`, correctly returns 200; changing that one too would be wrong.)

## 5. Loan list reads the wrong query parameter (`library/views.py`, line 60)

Wrong: `member_id = self.request.query_params.get("member_id")`. The documented filter is `?member=<id>`, so the filter is silently ignored and every member's loans come back.

Fix: `member_id = self.request.query_params.get("member")`

Shallow fix to watch for: changing the test to use `?member_id=` instead. Tests are correct; the hidden test uses `?member=`.

## Hidden tests (`_instructor/hidden_tests/`)

| Test | What it checks (from ARCHITECTURE.md) | Bugs |
|---|---|---|
| `test_hidden_loan_limit_is_inclusive` | member at `max_loans` (one loan overdue) is refused with 400, nothing created | 3 |
| `test_hidden_member_below_limit_can_borrow_and_returned_loans_do_not_count` | returned loans don't count toward the limit; 201 and full loan body (dates, `returned_on: null`) | 4 |
| `test_hidden_available_copies_track_open_loans_only` | `available_copies` on book detail; `?available=true` list filter | 1, 2 |
| `test_hidden_loan_list_filters_and_ordering` | `?member=` combined with `?status=active` / `overdue`; ordering by due date ascending | 5 |
| `test_hidden_catalog_writes_are_staff_only` | desk and anonymous POST refused, desk DELETE 403, staff DELETE 204, desk reads 200 | 1 |
| `test_hidden_late_return_fee_and_double_return` | 3 days late gives fee `"0.75"`; second return is 400 and fee unchanged | none (regression guard: passes on pristine; fails if a candidate breaks fee or double-return handling while fixing other bugs) |

Run them with `bash _instructor/run_hidden.sh <attempt-folder>`.
