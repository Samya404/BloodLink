from marshmallow import Schema, fields, validate
from schemas.blood_schema import VALID_BLOOD_GROUPS, VALID_COMPONENTS

class CreateRequestSchema(Schema):
    blood_group = fields.String(required=True, validate=validate.OneOf(VALID_BLOOD_GROUPS))
    component = fields.String(validate=validate.OneOf(VALID_COMPONENTS))
    units_required = fields.Integer(required=True, validate=validate.Range(min=1, max=50))
    hospital_id = fields.Integer()
    city = fields.String()
    required_by = fields.DateTime()
    priority = fields.String(validate=validate.OneOf(['NORMAL', 'URGENT', 'EMERGENCY']))
    notes = fields.String()

class UpdateRequestSchema(Schema):
    status = fields.String(validate=validate.OneOf(['OPEN', 'FULFILLED', 'CANCELLED']))
    notes = fields.String()

class RequestResponseSchema(Schema):
    id = fields.Integer(dump_only=True)
    blood_group = fields.String()
    component = fields.String()
    units_required = fields.Integer()
    hospital_id = fields.Integer()
    city = fields.String()
    required_by = fields.DateTime()
    priority = fields.String()
    notes = fields.String()
    status = fields.String()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
