from datetime import timedelta

from django.utils import timezone

from reviews.models import Member, Review, Violation


def header(member):
    return {"HTTP_X_USER_ID": str(member.id)}


def post_review(client, product, member, body, rating=3):
    return client.post(
        f"/api/products/{product.id}/reviews/",
        {"rating": rating, "body": body},
        format="json",
        **header(member),
    )


def test_hidden_banned_words_are_case_insensitive_whole_words(
    hidden_client, hidden_member, hidden_product
):
    writer = hidden_member("writer")

    blocked = post_review(hidden_client, hidden_product, writer, "SCAM alert. Total Ripoff!")
    assert blocked.status_code == 403
    assert blocked.json() == {"error": "review violates content policy"}
    violation = Violation.objects.get(member=writer)
    assert violation.words == ["ripoff", "scam"]

    allowed = post_review(hidden_client, hidden_product, writer, "Cooked scampi on it, Spamming rain all night.")
    assert allowed.status_code == 201
    writer.refresh_from_db()
    assert writer.violation_count == 1


def test_hidden_owner_edits_and_access_rules(
    hidden_client, hidden_member, hidden_product
):
    owner = hidden_member("owner")
    stranger = hidden_member("stranger")
    review = Review.objects.create(
        product=hidden_product, author=owner, rating=2, body="Leaks in heavy rain."
    )
    url = f"/api/reviews/{review.id}/"

    assert hidden_client.patch(url, {"rating": 5}, format="json").status_code == 401
    missing = hidden_client.patch("/api/reviews/999999/", {"rating": 5}, format="json", **header(owner))
    assert missing.status_code == 404
    assert missing.json() == {"error": "review not found"}

    other = hidden_client.patch(url, {"rating": 5}, format="json", **header(stranger))
    assert other.status_code == 403
    assert other.json() == {"error": "forbidden"}

    empty = hidden_client.patch(url, {}, format="json", **header(owner))
    assert empty.status_code == 400
    assert empty.json() == {"error": "rating or body is required"}

    before = Review.objects.get(pk=review.id).updated_at
    rating_only = hidden_client.patch(url, {"rating": 4}, format="json", **header(owner))
    assert rating_only.status_code == 200
    review.refresh_from_db()
    assert review.rating == 4
    assert review.body == "Leaks in heavy rain."

    new_body = hidden_client.patch(url, {"body": "Seams fixed it, now dry."}, format="json", **header(owner))
    assert new_body.status_code == 200
    assert new_body.json()["body"] == "Seams fixed it, now dry."
    review.refresh_from_db()
    assert review.body == "Seams fixed it, now dry."
    assert review.updated_at >= before
    owner.refresh_from_db()
    assert owner.violation_count == 0


def test_hidden_flag_threshold_and_status_endpoint(
    hidden_client, hidden_member, hidden_product
):
    member = hidden_member("repeat")
    status_url = f"/api/members/{member.id}/moderation/"

    post_review(hidden_client, hidden_product, member, "spam")
    post_review(hidden_client, hidden_product, member, "counterfeit spam")
    two = hidden_client.get(status_url, **header(member)).json()
    assert two["violation_count"] == 2
    assert two["is_flagged"] is False

    post_review(hidden_client, hidden_product, member, "scam")
    three = hidden_client.get(status_url, **header(member)).json()
    assert three["violation_count"] == 3
    assert three["is_flagged"] is True
    assert [v["words"] for v in three["violations"]] == [["scam"], ["counterfeit", "spam"], ["spam"]]
    assert all(v["action"] == "create" and v["review_id"] is None for v in three["violations"])
    assert Member.objects.get(pk=member.id).is_flagged is True


def test_hidden_only_the_flag_blocks(hidden_client, hidden_member, hidden_product):
    manually_flagged = hidden_member("flagged-by-mod", is_flagged=True, violation_count=0)
    own_review = Review.objects.create(
        product=hidden_product, author=manually_flagged, rating=3, body="Okay."
    )

    post = post_review(hidden_client, hidden_product, manually_flagged, "Fine tent.")
    assert post.status_code == 403
    assert post.json() == {"error": "account is flagged"}

    bad_rating = post_review(hidden_client, hidden_product, manually_flagged, "Fine tent.", rating=9)
    assert bad_rating.status_code == 403
    assert bad_rating.json() == {"error": "account is flagged"}

    edit = hidden_client.patch(
        f"/api/reviews/{own_review.id}/", {"rating": 5}, format="json", **header(manually_flagged)
    )
    assert edit.status_code == 403
    assert edit.json() == {"error": "account is flagged"}

    unflagged = hidden_member("cleared", is_flagged=False, violation_count=5)
    allowed = post_review(hidden_client, hidden_product, unflagged, "Back to normal.")
    assert allowed.status_code == 201


def test_hidden_list_ordering_ties_and_missing_product(
    hidden_client, hidden_member, hidden_product
):
    author = hidden_member("lister")
    same_time = timezone.now() - timedelta(hours=1)
    first = Review.objects.create(product=hidden_product, author=author, rating=3, body="A", created_at=same_time)
    second = Review.objects.create(product=hidden_product, author=author, rating=3, body="B", created_at=same_time)
    newest = Review.objects.create(product=hidden_product, author=author, rating=3, body="C")

    response = hidden_client.get(f"/api/products/{hidden_product.id}/reviews/")
    assert response.status_code == 200
    assert [r["id"] for r in response.json()] == [newest.id, second.id, first.id]

    missing = hidden_client.get("/api/products/999999/reviews/")
    assert missing.status_code == 404
    assert missing.json() == {"error": "product not found"}


def test_hidden_moderation_status_access(hidden_client, hidden_member):
    member = hidden_member("quiet")
    other = hidden_member("nosy")
    url = f"/api/members/{member.id}/moderation/"

    anonymous = hidden_client.get(url)
    assert anonymous.status_code == 401
    assert anonymous.json() == {"error": "authentication required"}

    forbidden = hidden_client.get(url, **header(other))
    assert forbidden.status_code == 403
    assert forbidden.json() == {"error": "forbidden"}

    own = hidden_client.get(url, **header(member))
    assert own.status_code == 200
    assert own.json() == {"violation_count": 0, "is_flagged": False, "violations": []}
