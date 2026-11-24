from datetime import timedelta

from django.utils import timezone

from library.models import Book, Loan


def test_hidden_loan_limit_is_inclusive(h_desk, h_book, h_member, h_loan):
    member = h_member(max_loans=2)
    h_loan(h_book(), member)
    h_loan(h_book(), member, due_in_days=-3)
    target = h_book(total_copies=5)

    response = h_desk.post("/api/loans/", {"book": target.id, "member": member.id}, format="json")

    assert response.status_code == 400
    assert Loan.objects.filter(member=member).count() == 2


def test_hidden_member_below_limit_can_borrow_and_returned_loans_do_not_count(
    h_desk, h_book, h_member, h_loan
):
    member = h_member(max_loans=2)
    h_loan(h_book(), member)
    h_loan(h_book(), member, returned_on=timezone.localdate())
    target = h_book()

    response = h_desk.post("/api/loans/", {"book": target.id, "member": member.id}, format="json")

    assert response.status_code == 201
    body = response.json()
    assert body["book"] == target.id
    assert body["member"] == member.id
    assert body["borrowed_on"] == timezone.localdate().isoformat()
    assert body["due_date"] == (timezone.localdate() + timedelta(days=14)).isoformat()
    assert body["returned_on"] is None


def test_hidden_available_copies_track_open_loans_only(h_desk, h_book, h_member, h_loan):
    book = h_book(total_copies=3)
    h_loan(book, h_member())
    h_loan(book, h_member(), returned_on=timezone.localdate())
    h_loan(book, h_member(), returned_on=timezone.localdate())

    detail = h_desk.get(f"/api/books/{book.id}/")
    assert detail.status_code == 200
    assert detail.json()["available_copies"] == 2

    full = h_book(total_copies=1)
    h_loan(full, h_member())
    listed = h_desk.get("/api/books/?available=true").json()
    ids = {b["id"] for b in listed}
    assert book.id in ids
    assert full.id not in ids


def test_hidden_loan_list_filters_and_ordering(h_desk, h_book, h_member, h_loan):
    alice = h_member(name="Alice")
    bob = h_member(name="Bob")
    late = h_loan(h_book(), alice, due_in_days=-2)
    later = h_loan(h_book(), alice, due_in_days=10)
    soon = h_loan(h_book(), alice, due_in_days=1)
    h_loan(h_book(), alice, due_in_days=-20, returned_on=timezone.localdate())
    h_loan(h_book(), bob, due_in_days=-5)

    response = h_desk.get(f"/api/loans/?member={alice.id}&status=active")
    assert response.status_code == 200
    assert [loan["id"] for loan in response.json()] == [soon.id, later.id]

    overdue = h_desk.get(f"/api/loans/?member={alice.id}&status=overdue").json()
    assert [loan["id"] for loan in overdue] == [late.id]
    assert overdue[0]["status"] == "overdue"


def test_hidden_catalog_writes_are_staff_only(h_staff, h_desk, h_anon, h_book):
    payload = {
        "title": "Refactoring",
        "author": "Martin Fowler",
        "isbn": "9780134757599",
        "total_copies": 1,
    }

    assert h_desk.post("/api/books/", payload, format="json").status_code == 403
    assert h_anon.post("/api/books/", payload, format="json").status_code in (401, 403)
    assert not Book.objects.filter(isbn="9780134757599").exists()

    book = h_book()
    assert h_desk.get("/api/books/").status_code == 200
    assert h_desk.get(f"/api/books/{book.id}/").status_code == 200
    assert h_desk.delete(f"/api/books/{book.id}/").status_code == 403
    assert h_staff.delete(f"/api/books/{book.id}/").status_code == 204


def test_hidden_late_return_fee_and_double_return(h_desk, h_book, h_member, h_loan):
    loan = h_loan(h_book(), h_member(), due_in_days=-3)

    first = h_desk.post(f"/api/loans/{loan.id}/return/")
    assert first.status_code == 200
    assert first.json()["late_fee"] == "0.75"
    assert first.json()["status"] == "returned"

    second = h_desk.post(f"/api/loans/{loan.id}/return/")
    assert second.status_code == 400
    loan.refresh_from_db()
    assert str(loan.late_fee) == "0.75"
