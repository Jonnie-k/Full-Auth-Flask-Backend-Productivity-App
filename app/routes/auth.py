from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from marshmallow import ValidationError
from app import db
from app.models.user import User
from app.schemas import signup_schema

auth_bp = Blueprint("auth", __name__)

# In-memory token blocklist for logout support
token_blocklist = set()


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    try:
        validated = signup_schema.load(data)
        signup_schema.validate_unique(validated)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 422

    user = User(username=validated["username"], email=validated["email"])
    user.password = validated["password"]
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"user": user.to_dict(), "access_token": token}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username or password."}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"user": user.to_dict(), "access_token": token}), 200


@auth_bp.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    token_blocklist.add(jti)
    return jsonify({"message": "Successfully logged out."}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found."}), 404
    return jsonify(user.to_dict()), 200
