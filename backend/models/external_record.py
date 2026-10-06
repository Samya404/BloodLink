from datetime import datetime, timezone
from extensions import db

class ExternalBloodRecord(db.Model):
    __tablename__ = 'external_blood_records'

    id = db.Column(db.Integer, primary_key=True)
    provider_name = db.Column(db.String(100), nullable=False) # e.g. 'Open Government Data (data.gov.in)'
    external_record_id = db.Column(db.String(100), nullable=True)
    blood_bank_name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=True, default='Government') # Government, Red Cross, Charitable, Private
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    district = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    pincode = db.Column(db.String(20), nullable=True)
    phone = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    blood_group = db.Column(db.String(5), nullable=False)
    component = db.Column(db.String(50), nullable=False)
    units_available = db.Column(db.Integer, default=0)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    source_updated_at = db.Column(db.DateTime, nullable=True)
    fetched_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    raw_reference = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'provider_name': self.provider_name,
            'blood_bank_name': self.blood_bank_name,
            'category': self.category,
            'address': self.address,
            'city': self.city,
            'district': self.district,
            'state': self.state,
            'pincode': self.pincode,
            'phone': self.phone,
            'email': self.email,
            'blood_group': self.blood_group,
            'component': self.component,
            'units_available': self.units_available,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'source_updated_at': self.source_updated_at.isoformat() if self.source_updated_at else None,
            'fetched_at': self.fetched_at.isoformat() if self.fetched_at else None
        }
