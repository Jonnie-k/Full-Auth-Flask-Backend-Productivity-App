from app.models.note import Note


def create_note(client, headers, title="Test Note", content="Some content", category="general"):
    return client.post("/notes", json={
        "title": title,
        "content": content,
        "category": category,
    }, headers=headers)


def test_create_note(client, auth_headers):
    resp = create_note(client, auth_headers)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["title"] == "Test Note"
    assert data["category"] == "general"


def test_create_note_missing_fields(client, auth_headers):
    resp = client.post("/notes", json={"title": "No content"}, headers=auth_headers)
    assert resp.status_code == 422


def test_create_note_unauthenticated(client):
    resp = client.post("/notes", json={"title": "x", "content": "y"})
    assert resp.status_code == 401


def test_get_notes_paginated(client, auth_headers, db):
    from app.models.user import User
    user = User.query.filter_by(username="tester").first()
    for i in range(15):
        note = Note(title=f"Note {i}", content="content", user_id=user.id)
        db.session.add(note)
    db.session.commit()

    resp = client.get("/notes?page=1&per_page=10", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["notes"]) == 10
    assert data["total"] == 15
    assert data["pages"] == 2

    resp2 = client.get("/notes?page=2&per_page=10", headers=auth_headers)
    assert len(resp2.get_json()["notes"]) == 5


def test_get_single_note(client, auth_headers):
    create_resp = create_note(client, auth_headers, title="Single Note")
    note_id = create_resp.get_json()["id"]

    resp = client.get(f"/notes/{note_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "Single Note"


def test_get_note_not_found(client, auth_headers):
    resp = client.get("/notes/9999", headers=auth_headers)
    assert resp.status_code == 404


def test_update_note(client, auth_headers):
    note_id = create_note(client, auth_headers).get_json()["id"]

    resp = client.patch(f"/notes/{note_id}", json={"title": "Updated Title", "is_pinned": True}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["title"] == "Updated Title"
    assert data["is_pinned"] is True


def test_update_note_not_owned(client, db, auth_headers):
    from app.models.user import User
    other = User(username="other", email="other@test.com")
    other.password = "pass123"
    db.session.add(other)
    db.session.commit()

    note = Note(title="Other's note", content="private", user_id=other.id)
    db.session.add(note)
    db.session.commit()

    resp = client.patch(f"/notes/{note.id}", json={"title": "Hacked"}, headers=auth_headers)
    assert resp.status_code == 404


def test_delete_note(client, auth_headers):
    note_id = create_note(client, auth_headers).get_json()["id"]

    resp = client.delete(f"/notes/{note_id}", headers=auth_headers)
    assert resp.status_code == 200

    resp2 = client.get(f"/notes/{note_id}", headers=auth_headers)
    assert resp2.status_code == 404


def test_delete_note_not_owned(client, db, auth_headers):
    from app.models.user import User
    other = User(username="another", email="another@test.com")
    other.password = "pass123"
    db.session.add(other)
    db.session.commit()

    note = Note(title="Private", content="private", user_id=other.id)
    db.session.add(note)
    db.session.commit()

    resp = client.delete(f"/notes/{note.id}", headers=auth_headers)
    assert resp.status_code == 404
