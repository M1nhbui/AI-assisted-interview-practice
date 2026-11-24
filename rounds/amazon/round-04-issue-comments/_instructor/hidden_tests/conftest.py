import pytest
from rest_framework.test import APIClient

from tracker.models import Issue, Member


@pytest.fixture
def hidden_client():
    return APIClient()


@pytest.fixture
def hidden_member(db):
    def _make(username, **overrides):
        return Member.objects.create(username=username, **overrides)

    return _make


@pytest.fixture
def hidden_issue(hidden_member):
    owner = hidden_member("hidden-reporter")
    return Issue.objects.create(title="Hidden issue", reporter=owner)
