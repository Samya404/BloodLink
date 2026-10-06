from marshmallow import Schema, fields, validate

VALID_BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
VALID_COMPONENTS = ['WHOLE_BLOOD', 'PACKED_RED_CELLS', 'PLASMA', 'PLATELETS']

class BloodAvailabilityQuerySchema(Schema):
    blood_group = fields.String(validate=validate.OneOf(VALID_BLOOD_GROUPS), required=False)
    component = fields.String(validate=validate.OneOf(VALID_COMPONENTS), required=False)
    city = fields.String(required=False)
    state = fields.String(required=False)
    source = fields.String(required=False)

class BloodAvailabilityResponseSchema(Schema):
    blood_bank = fields.String()
    location = fields.String()
    blood_group = fields.String()
    component = fields.String()
    available_units = fields.Integer()
    source = fields.String()
    last_updated = fields.DateTime()
    data_freshness = fields.String()
