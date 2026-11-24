from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from library.models import Book, Loan, Member


@pytest.fixture
def h_staff(db):
    user = get_user_model().objects.create_user(
        username="h_staff", password="x", is_staff=True
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def h_desk(db):
    user = get_user_model().objects.create_user(username="h_desk", password="x")
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def h_anon(db):
    return APIClient()


@pytest.fixture
def h_book(db):
    seq = {"n": 0}

    def make(**kw):
        seq["n"] += 1
        data = {
            "title": f"Hidden Book {seq['n']}",
            "author": "Hidden Author",
            "isbn": f"979111111{seq['n']:04d}",
            "total_copies": 1,
        }
        data.update(kw)
        return Book.objects.create(**data)

    return make


@pytest.fixture
def h_member(db):
    seq = {"n": 0}

    def make(**kw):
        seq["n"] += 1
        data = {"name": f"Hidden Member {seq['n']}", "email": f"hidden{seq['n']}@example.org"}
        data.update(kw)
        return Member.objects.create(**data)

    return make


@pytest.fixture
def h_loan(db):
    def make(book, member, due_in_days=14, returned_on=None):
        today = timezone.localdate()
        due = today + timedelta(days=due_in_days)
        return Loan.objects.create(
            book=book,
            member=member,
            borrowed_on=due - timedelta(days=14),
            due_date=due,
            returned_on=returned_on,
        )

    return make
