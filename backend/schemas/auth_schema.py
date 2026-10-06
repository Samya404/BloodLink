from marshmallow import Schema, fields, validate

class RegisterSchema(Schema):
    full_name = fields.String(required=True, validate=validate.Length(min=2, max=150))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))
    phone = fields.String(required=False)
    role = fields.String(required=True, validate=validate.OneOf(['PATIENT', 'DONOR', 'HOSPITAL']))

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    full_name = fields.String()
    email = fields.Email()
    phone = fields.String()
    role = fields.String()
    is_active = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
