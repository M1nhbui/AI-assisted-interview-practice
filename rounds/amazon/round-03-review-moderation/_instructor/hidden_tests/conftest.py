import pytest
from rest_framework.test import APIClient

from reviews.models import Member, Product


@pytest.fixture
def hidden_client():
    return APIClient()


@pytest.fixture
def hidden_member(db):
    def _make(username, **overrides):
        return Member.objects.create(username=username, **overrides)

    return _make


@pytest.fixture
def hidden_product(db):
    return Product.objects.create(name="Hidden Test Tent")
