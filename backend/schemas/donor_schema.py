from marshmallow import Schema, fields, validate
from schemas.blood_schema import VALID_BLOOD_GROUPS

class DonorProfileSchema(Schema):
    blood_group = fields.String(validate=validate.OneOf(VALID_BLOOD_GROUPS))
    city = fields.String()
    area = fields.String()
    availability_status = fields.String(validate=validate.OneOf(['AVAILABLE', 'UNAVAILABLE']))
    latitude = fields.Float()
    longitude = fields.Float()

class UpdateAvailabilitySchema(Schema):
    availability_status = fields.String(validate=validate.OneOf(['AVAILABLE', 'UNAVAILABLE']), required=True)

class DonorMatchResponseSchema(Schema):
    donor_id = fields.Integer()
    blood_group = fields.String()
    approximate_distance = fields.Float()
    availability = fields.String()
    match_score = fields.Integer()
    reason = fields.String()
