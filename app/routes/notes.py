from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app import db
from app.models.note import Note
from app.schemas import note_schema, notes_schema

notes_bp = Blueprint("notes", __name__)


@notes_bp.route("", methods=["GET"])
@jwt_required()
def get_notes():
    user_id = int(get_jwt_identity())
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 50)

    pagination = (
        Note.query.filter_by(user_id=user_id)
        .order_by(Note.is_pinned.desc(), Note.updated_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return jsonify({
        "notes": notes_schema.dump(pagination.items),
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page,
        "per_page": pagination.per_page,
    }), 200


@notes_bp.route("/<int:note_id>", methods=["GET"])
@jwt_required()
def get_note(note_id):
    user_id = int(get_jwt_identity())
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()
    if not note:
        return jsonify({"error": "Note not found."}), 404
    return jsonify(note_schema.dump(note)), 200


@notes_bp.route("", methods=["POST"])
@jwt_required()
def create_note():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    try:
        validated = note_schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    note = Note(user_id=user_id, **validated)
    db.session.add(note)
    db.session.commit()
    return jsonify(note_schema.dump(note)), 201


@notes_bp.route("/<int:note_id>", methods=["PATCH"])
@jwt_required()
def update_note(note_id):
    user_id = int(get_jwt_identity())
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()
    if not note:
        return jsonify({"error": "Note not found."}), 404

    data = request.get_json()
    try:
        validated = note_schema.load(data, partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    for key, value in validated.items():
        setattr(note, key, value)

    db.session.commit()
    return jsonify(note_schema.dump(note)), 200


@notes_bp.route("/<int:note_id>", methods=["DELETE"])
@jwt_required()
def delete_note(note_id):
    user_id = int(get_jwt_identity())
    note = Note.query.filter_by(id=note_id, user_id=user_id).first()
    if not note:
        return jsonify({"error": "Note not found."}), 404

    db.session.delete(note)
    db.session.commit()
    return jsonify({"message": "Note deleted."}), 200
