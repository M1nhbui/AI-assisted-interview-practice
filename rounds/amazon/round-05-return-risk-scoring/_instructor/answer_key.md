# Answer key: amazon / round-05-return-risk-scoring

Based on reported variant: **Return-system fraud scoring**: items flagged as non-returnable by a risk score over rating, item value and account age, with about six numeric threshold and weighting bugs along the scoring path, plus an unfinished function (reports of "unfinished functions" in the C++ return engine, and HackerRank's feature-building task type).

Format: Amazon's official demo (two-line TASK.md, issue in README.md). **Visible tests only**: no hidden tests this round, by request. Every bug is caught by at least one visible test.

Weakness bias: README rules with exact boundaries (round 3's shallow `>=` fix), many small bugs under time pressure, and a first taste of writing a missing function.

6 planted bugs (all in `returns/scoring.py`) + 1 unfinished function. Several tests fail for more than one reason, as candidates report for this variant: fixing one bug often moves a score without making the test pass yet.

Visible tests on pristine: 1 passed, 6 failed.

| # | Listed? | File:line | Defect shape | Tests that fail if only this is left broken |
|---|---|---|---|---|
| 1 | Unlisted | `returns/scoring.py:19` | boundary: `<= 200` puts $200 in the 15-point tier | `test_item_value_tiers` |
| 2 | Partly ("low-risk returns get high scores") | `returns/scoring.py:27-31` | weighting inverted: low ratings (1-2) get 20, high (4-5) get 0 | low_risk, item_value_tiers, new_account_and_positive_rating, recent_return_history, decision_thresholds |
| 3 | Partly (same symptom) | `returns/scoring.py:36` | unit bug: `timedelta.seconds` (seconds part of the day) instead of `.days` | low_risk, item_value_tiers, new_account_and_positive_rating, recent_return_history, decision_thresholds |
| 4 | LISTED: "no recent returns still get history points" (together with 5) | `returns/scoring.py:47` | inverted date filter: `created_at__lte` counts returns OLDER than 90 days | `test_recent_return_history_adds_risk`, `test_decision_thresholds` |
| 5 | LISTED (same symptom) | `returns/scoring.py:48` | `max` instead of `min`: everyone gets at least the 20-point cap | low_risk, item_value_tiers, new_account_and_positive_rating, recent_return_history, decision_thresholds |
| 6 | Unlisted | `returns/scoring.py:52` | boundary: `score <= 40` approves a score of exactly 40 | `test_decision_thresholds` |
| 7 | LISTED: "summary endpoint never finished" | `returns/services.py:33` | unfinished function: `raise NotImplementedError` | `test_return_summary` |

## Fixes

1. `if price < Decimal("200"):`
2. `rating_points`: `if item_rating >= 4: return 20`, `if item_rating == 3: return 10`, else `0`.
3. `account_age_days = (now - customer.account_created_at).days`. (`timedelta.seconds` is only the 0 to 86399 seconds part, not the total. `total_seconds() / 86400` also works if you floor it.)
4. `filter(created_at__gte=window_start)`.
5. `return min(recent_returns * HISTORY_POINTS_PER_RETURN, HISTORY_POINTS_CAP)`.
6. `if score < MANUAL_REVIEW_FROM:`
7. One correct implementation:

```python
def summarize_returns(customer):
    returns = list(customer.return_requests.all())
    summary = {
        "total": len(returns),
        "approved": 0,
        "manual_review": 0,
        "non_returnable": 0,
        "average_risk_score": None,
    }
    for return_request in returns:
        summary[return_request.decision] += 1
    if returns:
        total_score = sum(r.risk_score for r in returns)
        summary["average_risk_score"] = round(total_score / len(returns), 2)
    return summary
```

(An ORM version with `aggregate(Avg("risk_score"))` and `Count` works too, as long as the empty case returns `null` and all three counts are present.)

## Traps

- Tuning numbers until one test passes. Test scores depend on all four components, so check each component against the README with a breakpoint: `p value_points(item.price), rating_points(item_rating), account_points(customer, now), history_points(customer, now)`.
- `history_points`: fixing only the cap (5) or only the filter (4) still leaves `test_recent_return_history_adds_risk` failing.
- Summary: forgetting the empty case (`average_risk_score: null`, counts 0), or returning a Decimal/str instead of a number.

Verified: with all fixes, 7/7 pass. Reverting any single fix fails exactly the tests in the table.
