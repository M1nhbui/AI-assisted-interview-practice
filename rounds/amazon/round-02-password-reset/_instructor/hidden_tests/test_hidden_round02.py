from accounts.models import Account, ResetCode

REQUEST_URL = "/api/password-reset/request/"
VERIFY_URL = "/api/password-reset/verify/"
CONFIRM_URL = "/api/password-reset/confirm/"
LOGIN_URL = "/api/login/"


def _post(client, url, data):
    return client.post(url, data, format="json")


def test_hidden_full_reset_flow(h_client, h_account):
    acct = h_account(password="original99")

    requested = _post(h_client, REQUEST_URL, {"email": acct.email})
    assert requested.status_code == 201
    code = ResetCode.objects.get(account=acct, used=False).code

    verified = _post(h_client, VERIFY_URL, {"email": acct.email, "code": code})
    assert verified.status_code == 200
    assert verified.json() == {"message": "Code verified"}

    confirmed = _post(
        h_client,
        CONFIRM_URL,
        {"email": acct.email, "code": code, "new_password": "replacement99"},
    )
    assert confirmed.status_code == 200
    assert confirmed.json() == {"message": "Password updated"}

    assert _post(h_client, LOGIN_URL, {"email": acct.email, "password": "replacement99"}).status_code == 200
    old = _post(h_client, LOGIN_URL, {"email": acct.email, "password": "original99"})
    assert old.status_code == 401
    assert old.json() == {"error": "invalid credentials"}


def test_hidden_code_expiry_window_is_thirty_seconds(h_client, h_account, h_code):
    acct = h_account()
    h_code(acct, code="111111", age_seconds=25)
    fresh = _post(h_client, VERIFY_URL, {"email": acct.email, "code": "111111"})
    assert fresh.status_code == 200

    other = h_account()
    stale = h_code(other, code="222222", age_seconds=35)
    expired = _post(h_client, VERIFY_URL, {"email": other.email, "code": "222222"})
    assert expired.status_code == 410
    assert expired.json() == {"error": "code expired"}
    stale.refresh_from_db()
    assert stale.verified is False


def test_hidden_password_minimum_length_is_inclusive(h_client, h_account, h_code):
    ok = _post(h_client, "/api/accounts/", {"email": "eight@example.org", "password": "abcd1234"})
    assert ok.status_code == 201

    short = _post(h_client, "/api/accounts/", {"email": "seven@example.org", "password": "abc1234"})
    assert short.status_code == 400
    assert short.json() == {"error": "password must be at least 8 characters"}
    assert not Account.objects.filter(email="seven@example.org").exists()

    acct = h_account()
    h_code(acct, code="333333", verified=True)
    too_short = _post(
        h_client, CONFIRM_URL, {"email": acct.email, "code": "333333", "new_password": "zyx9876"}
    )
    assert too_short.status_code == 400
    assert too_short.json() == {"error": "password must be at least 8 characters"}

    exact = _post(
        h_client, CONFIRM_URL, {"email": acct.email, "code": "333333", "new_password": "zyxw9876"}
    )
    assert exact.status_code == 200
    assert _post(h_client, LOGIN_URL, {"email": acct.email, "password": "zyxw9876"}).status_code == 200


def test_hidden_account_detail_access_rules(h_client, h_account):
    owner = h_account()
    stranger = h_account()
    url = f"/api/accounts/{owner.id}/"

    mine = h_client.get(url, HTTP_X_USER_ID=str(owner.id))
    assert mine.status_code == 200
    assert mine.json()["id"] == owner.id
    assert mine.json()["email"] == owner.email
    assert "password" not in mine.json()

    assert h_client.get(url, HTTP_X_USER_ID="abc").status_code == 401
    assert h_client.get(url, HTTP_X_USER_ID="999999").status_code == 401

    theirs = h_client.get(f"/api/accounts/{stranger.id}/", HTTP_X_USER_ID=str(owner.id))
    assert theirs.status_code == 403
    assert theirs.json() == {"error": "forbidden"}


def test_hidden_reset_request_errors_and_code_rotation(h_client, h_account):
    missing = _post(h_client, REQUEST_URL, {})
    assert missing.status_code == 400
    assert missing.json() == {"error": "email is required"}

    unknown = _post(h_client, REQUEST_URL, {"email": "nobody@example.org"})
    assert unknown.status_code == 404
    assert unknown.json() == {"error": "account not found"}

    acct = h_account()
    assert _post(h_client, REQUEST_URL, {"email": acct.email}).status_code == 201
    first = ResetCode.objects.get(account=acct, used=False)
    assert _post(h_client, REQUEST_URL, {"email": acct.email}).status_code == 201
    first.refresh_from_db()
    assert first.used is True
    assert ResetCode.objects.filter(account=acct, used=False).count() == 1

    latest = ResetCode.objects.get(account=acct, used=False)
    if latest.code != first.code:
        stale = _post(h_client, VERIFY_URL, {"email": acct.email, "code": first.code})
        assert stale.status_code == 400
        assert stale.json() == {"error": "invalid code"}


def test_hidden_confirm_requires_verified_unused_code(h_client, h_account, h_code):
    acct = h_account(password="keepthis99")
    h_code(acct, code="444444")

    unverified = _post(
        h_client, CONFIRM_URL, {"email": acct.email, "code": "444444", "new_password": "newsecret99"}
    )
    assert unverified.status_code == 400
    assert unverified.json() == {"error": "code not verified"}

    missing = _post(h_client, CONFIRM_URL, {"email": acct.email, "code": "444444"})
    assert missing.status_code == 400
    assert missing.json() == {"error": "email, code and new_password are required"}

    assert _post(h_client, VERIFY_URL, {"email": acct.email, "code": "444444"}).status_code == 200
    assert _post(
        h_client, CONFIRM_URL, {"email": acct.email, "code": "444444", "new_password": "newsecret99"}
    ).status_code == 200

    reused = _post(
        h_client, CONFIRM_URL, {"email": acct.email, "code": "444444", "new_password": "another999"}
    )
    assert reused.status_code == 400
    assert reused.json() == {"error": "invalid code"}

    nobody = _post(h_client, VERIFY_URL, {"email": "ghost@example.org", "code": "444444"})
    assert nobody.status_code == 404
    assert nobody.json() == {"error": "account not found"}
