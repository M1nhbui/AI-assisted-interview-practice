from datetime import timedelta

from django.utils import timezone

from tracker.models import Comment, Issue


def header(member):
    return {"HTTP_X_USER_ID": str(member.id)}


def new_comment(issue, author, body, minutes_ago=0):
    return Comment.objects.create(
        issue=issue, author=author, body=body,
        created_at=timezone.now() - timedelta(minutes=minutes_ago),
    )


def test_hidden_body_whitespace_is_trimmed(hidden_client, hidden_member, hidden_issue):
    writer = hidden_member("writer")
    url = f"/api/issues/{hidden_issue.id}/comments/"

    blank = hidden_client.post(url, {"body": "   \n  "}, format="json", **header(writer))
    assert blank.status_code == 400
    assert blank.json() == {"error": "body is required"}
    assert Comment.objects.count() == 0

    padded = hidden_client.post(url, {"body": "  Looks fixed in 414.  "}, format="json", **header(writer))
    assert padded.status_code == 201
    assert padded.json()["body"] == "Looks fixed in 414."
    assert Comment.objects.get().body == "Looks fixed in 414."

    comment = Comment.objects.get()
    blank_edit = hidden_client.patch(f"/api/comments/{comment.id}/", {"body": "   "}, format="json", **header(writer))
    assert blank_edit.status_code == 400
    assert blank_edit.json() == {"error": "body is required"}


def test_hidden_delete_rules_and_deleted_is_not_found(hidden_client, hidden_member, hidden_issue):
    author = hidden_member("author")
    admin = hidden_member("admin", is_admin=True)
    stranger = hidden_member("stranger")
    comment = new_comment(hidden_issue, author, "Admin should be able to remove this.")
    url = f"/api/comments/{comment.id}/"

    assert hidden_client.delete(url).status_code == 401
    stranger_try = hidden_client.delete(url, **header(stranger))
    assert stranger_try.status_code == 403
    assert stranger_try.json() == {"error": "forbidden"}
    reporter_try = hidden_client.delete(url, **header(hidden_issue.reporter))
    assert reporter_try.status_code == 403

    admin_edit = hidden_client.patch(url, {"body": "Admin rewrite."}, format="json", **header(admin))
    assert admin_edit.status_code == 403
    assert admin_edit.json() == {"error": "forbidden"}

    assert hidden_client.delete(url, **header(admin)).status_code == 204
    again = hidden_client.delete(url, **header(admin))
    assert again.status_code == 404
    assert again.json() == {"error": "comment not found"}
    edit_deleted = hidden_client.patch(url, {"body": "Back?"}, format="json", **header(author))
    assert edit_deleted.status_code == 404


def test_hidden_only_the_author_edits(hidden_client, hidden_member, hidden_issue):
    other = hidden_member("other-dev")
    theirs = new_comment(hidden_issue, other, "Bisected to commit a1b2.")
    own = new_comment(hidden_issue, hidden_issue.reporter, "Thanks, assigning.")

    blocked = hidden_client.patch(
        f"/api/comments/{theirs.id}/", {"body": "Changed by reporter."}, format="json", **header(hidden_issue.reporter)
    )
    assert blocked.status_code == 403
    theirs.refresh_from_db()
    assert theirs.body == "Bisected to commit a1b2."
    assert theirs.edited is False

    allowed = hidden_client.patch(
        f"/api/comments/{own.id}/", {"body": "Thanks, assigned to Dev."}, format="json", **header(hidden_issue.reporter)
    )
    assert allowed.status_code == 200
    own.refresh_from_db()
    assert own.body == "Thanks, assigned to Dev."
    assert own.edited is True


def test_hidden_list_order_and_counts_skip_deleted(hidden_client, hidden_member, hidden_issue):
    viewer = hidden_member("viewer")
    same_time = timezone.now() - timedelta(minutes=30)
    first = Comment.objects.create(issue=hidden_issue, author=viewer, body="A", created_at=same_time)
    second = Comment.objects.create(issue=hidden_issue, author=viewer, body="B", created_at=same_time)
    gone = new_comment(hidden_issue, viewer, "C", minutes_ago=20)
    latest = new_comment(hidden_issue, viewer, "D", minutes_ago=1)
    Comment.objects.filter(pk=gone.pk).update(is_deleted=True)
    other_issue = Issue.objects.create(title="Other", reporter=viewer)
    new_comment(other_issue, viewer, "Elsewhere")

    listing = hidden_client.get(f"/api/issues/{hidden_issue.id}/comments/", **header(viewer))
    assert [c["id"] for c in listing.json()] == [first.id, second.id, latest.id]
    detail = hidden_client.get(f"/api/issues/{hidden_issue.id}/", **header(viewer))
    assert detail.json()["comment_count"] == 3
    other_detail = hidden_client.get(f"/api/issues/{other_issue.id}/", **header(viewer))
    assert other_detail.json()["comment_count"] == 1


def test_hidden_edit_response_and_auth_variants(hidden_client, hidden_member, hidden_issue):
    author = hidden_member("editor")
    comment = new_comment(hidden_issue, author, "First draft.")
    url = f"/api/comments/{comment.id}/"

    for bad_header in ["", "abc", "123456"]:
        response = hidden_client.patch(url, {"body": "x"}, format="json", HTTP_X_USER_ID=bad_header)
        assert response.status_code == 401
        assert response.json() == {"error": "authentication required"}

    missing = hidden_client.patch("/api/comments/999999/", {"body": "x"}, format="json", **header(author))
    assert missing.status_code == 404

    edited = hidden_client.patch(url, {"body": "Second draft."}, format="json", **header(author))
    assert edited.status_code == 200
    body = edited.json()
    assert body["body"] == "Second draft."
    assert body["edited"] is True
    assert body["id"] == comment.id
    assert Comment.objects.get(pk=comment.id).body == "Second draft."


def test_hidden_issue_endpoints_and_closed_rule(hidden_client, hidden_member):
    member = hidden_member("checker")

    assert hidden_client.get("/api/issues/999999/", **header(member)).json() == {"error": "issue not found"}
    missing_post = hidden_client.post("/api/issues/999999/comments/", {"body": "hi"}, format="json", **header(member))
    assert missing_post.status_code == 404
    assert hidden_client.get("/api/issues/999999/comments/").status_code == 401

    closed = Issue.objects.create(title="Closed", reporter=member, status="closed")
    blocked = hidden_client.post(f"/api/issues/{closed.id}/comments/", {"body": "   "}, format="json", **header(member))
    assert blocked.status_code == 409
    assert blocked.json() == {"error": "issue is closed"}

    detail = hidden_client.get(f"/api/issues/{closed.id}/", **header(member))
    assert detail.status_code == 200
    assert detail.json()["status"] == "closed"
    assert detail.json()["comment_count"] == 0
