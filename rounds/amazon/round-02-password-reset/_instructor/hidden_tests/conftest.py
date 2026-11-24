from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import Account, ResetCode


@pytest.fixture
def h_client(db):
    return APIClient()


@pytest.fixture
def h_account(db):
    seq = {"n": 0}

    def make(password="hiddenpass99", **kw):
        seq["n"] += 1
        data = {"email": f"hidden{seq['n']}@example.org"}
        data.update(kw)
        acct = Account(**data)
        acct.set_password(password)
        acct.save()
        return acct

    return make


@pytest.fixture
def h_code(db):
    def make(account, code="654321", age_seconds=0, verified=False, used=False):
        return ResetCode.objects.create(
            account=account,
            code=code,
            generated_at=timezone.now() - timedelta(seconds=age_seconds),
            verified=verified,
            used=used,
        )

    return make
