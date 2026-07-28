from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
import os

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///notes_app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-key")

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    @app.errorhandler(404)
    def not_found(e):
        from flask import jsonify
        return jsonify({"error": "Resource not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        from flask import jsonify
        return jsonify({"error": "Method not allowed."}), 405

    @jwt.unauthorized_loader
    def missing_token_response(reason):
        from flask import jsonify
        return jsonify({"error": "Authorization token is missing or invalid."}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(reason):
        from flask import jsonify
        return jsonify({"error": "Token is invalid."}), 422

    from app.routes.auth import auth_bp, token_blocklist

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return jwt_payload["jti"] in token_blocklist

    @jwt.revoked_token_loader
    def revoked_token_response(jwt_header, jwt_payload):
        from flask import jsonify
        return jsonify({"error": "Token has been revoked. Please log in again."}), 401

    from app.routes.auth import auth_bp
    from app.routes.notes import notes_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(notes_bp, url_prefix="/notes")

    return app
