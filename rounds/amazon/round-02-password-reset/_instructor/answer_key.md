# Answer key: amazon / round-02-password-reset

Based on reported variant: **Password reset** (verification code never generated, verify skips the 30-second expiry window, reset password not persisted to the user profile, plus a broken test-support file that errors before tests run).

Coin flip for a broken test-support file: **heads**. `tests/conftest.py` uses `make_password` without importing it.

5 planted app bugs (3 LISTED in TASK.md, 2 UNLISTED) + 1 broken fixture. Line numbers refer to files in `pristine.tar.gz`.

Visible tests on the pristine repo: 1 passed, 5 errors (all 5 errors come from the `account` fixture). After fixing only the fixture: 2 passed, 4 failed.
Hidden tests on pristine: 5 of 6 fail (`test_hidden_confirm_requires_verified_unused_code` is a regression guard and passes).

| # | Listed? | File:line | Defect shape | Visible tests broken | Hidden tests broken |
|---|---|---|---|---|---|
| 0 | UNLISTED (fixture) | `tests/conftest.py:18` | undefined name in fixture | errors in 5 of 6 (every test using `account`) | none (hidden tests use their own fixtures) |
| 1 | LISTED: "never get a verification code they can use" | `accounts/services.py:14` | object built but never persisted | `test_request_reset_creates_code` | `test_hidden_full_reset_flow`, `test_hidden_reset_request_errors_and_code_rotation` |
| 2 | LISTED: "codes keep working long after the 30-second window" | `accounts/models.py:40` | skipped/broken time-window check (minutes instead of seconds) | `test_verify_rejects_expired_code` | `test_hidden_code_expiry_window_is_thirty_seconds` |
| 3 | LISTED: "can still only sign in with their old password" | `accounts/services.py:36` | change not persisted (field missing from `update_fields`) | `test_confirm_reset_persists_new_password` | `test_hidden_full_reset_flow`, `test_hidden_password_minimum_length_is_inclusive` (last step) |
| 4 | UNLISTED | `accounts/auth.py:14` | inverted comparison (401/403 rules) | `test_account_detail_requires_matching_user` | `test_hidden_account_detail_access_rules` |
| 5 | UNLISTED, hidden-only | `accounts/validators.py:7` | off-by-one in validation | none | `test_hidden_password_minimum_length_is_inclusive` |

Bugs outside the view: all five (services, models, auth helper, validators).

## 0. Broken fixture (`tests/conftest.py`, line 18)

`account` calls `make_password("oldpass123")`, but `make_password` is never imported. Every test that uses `account` errors at setup with `NameError: name 'make_password' is not defined`. The test assertions are correct.

Fix: add `from django.contrib.auth.hashers import make_password` to the imports. (Building the account with `Account(...)`, `set_password`, `save()` like `other_account` also works.)

Watch for: deleting or skipping the erroring tests. They must run.

## 1. Reset code never saved (`accounts/services.py`, lines 14-19)

Wrong:
```python
    reset_code = ResetCode(
        account=account,
        code=generate_code(),
        generated_at=timezone.now(),
    )
    return reset_code
```
The object is built in memory and returned but never written to the database. The view still answers 201, so the bug is silent; `verify` then always says `invalid code`.

Fix: `ResetCode.objects.create(...)` (or call `reset_code.save()` before returning).

## 2. Expiry window is 30 minutes, not 30 seconds (`accounts/models.py`, line 40)

Wrong: `return self.generated_at + timedelta(minutes=ttl)` with `ttl = settings.PASSWORD_RESET_CODE_TTL_SECONDS`. A 45-second-old code still verifies.

Fix: `timedelta(seconds=ttl)`.

Shallow fix to watch for: hard-coding an extra check in `VerifyCodeView` (e.g. `if timezone.now() - reset_code.generated_at > timedelta(seconds=30)`). It passes the tests but leaves `expires_at` / `is_expired()` wrong. Also watch for flipping the comparison in `is_expired`, which makes fresh codes expire.

## 3. New password not persisted (`accounts/services.py`, line 36)

Wrong: `account.save(update_fields=["password_changed_at"])`. `set_password` updates the hash in memory, but `update_fields` only writes `password_changed_at`, so the stored password stays the old one. The response is 200 and `password_changed_at` is set, so it looks fixed from the outside.

Fix: `account.save(update_fields=["password", "password_changed_at"])` (or plain `account.save()`).

## 4. Profile ownership check inverted (`accounts/auth.py`, line 14)

Wrong: `return requester.id != account_id`. The owner gets 403 and any other user can read the profile (200).

Fix: `return requester.id == account_id`.

Not mentioned in TASK.md. The visible test `test_account_detail_requires_matching_user` fails on it once the fixture is fixed. Missing / non-numeric / unknown `X-User-Id` already correctly gives 401.

## 5. Password minimum off by one (`accounts/validators.py`, line 7)

Wrong: `if len(value) <= MIN_PASSWORD_LENGTH:` rejects an 8-character password. README: "at least 8 characters".

Fix: `if len(value) < MIN_PASSWORD_LENGTH:`

No visible test covers it (all visible passwords are 10+ characters). It affects both registration and reset confirm. Finding it requires reading the README contract against `validators.py`.

## Full fix diff

```diff
--- tests/conftest.py
+from django.contrib.auth.hashers import make_password
--- accounts/models.py
-        return self.generated_at + timedelta(minutes=ttl)
+        return self.generated_at + timedelta(seconds=ttl)
--- accounts/services.py
-    reset_code = ResetCode(
+    reset_code = ResetCode.objects.create(
-    account.save(update_fields=["password_changed_at"])
+    account.save(update_fields=["password", "password_changed_at"])
--- accounts/auth.py
-    return requester.id != account_id
+    return requester.id == account_id
--- accounts/validators.py
-    if len(value) <= MIN_PASSWORD_LENGTH:
+    if len(value) < MIN_PASSWORD_LENGTH:
```

Verified: with this diff, 6/6 visible and 6/6 hidden pass. With every fix except #5, only `test_hidden_password_minimum_length_is_inclusive` fails.
