from marshmallow import Schema, fields, validate, ValidationError
from app.models.user import User


class SignupSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))

    def validate_unique(self, data):
        errors = {}
        if User.query.filter_by(username=data.get("username")).first():
            errors["username"] = ["Username already taken."]
        if User.query.filter_by(email=data.get("email")).first():
            errors["email"] = ["Email already registered."]
        if errors:
            raise ValidationError(errors)
        return data


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(dump_only=True)
    email = fields.Email(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class NoteSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    content = fields.Str(required=True, validate=validate.Length(min=1))
    category = fields.Str(validate=validate.OneOf(["general", "work", "personal", "ideas"]))
    is_pinned = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    user_id = fields.Int(dump_only=True)


signup_schema = SignupSchema()
user_schema = UserSchema()
note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)
