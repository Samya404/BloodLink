from datetime import datetime, timezone
from extensions import db

class DonorProfile(db.Model):
    __tablename__ = 'donor_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    blood_group = db.Column(db.String(5), nullable=False, index=True)
    city = db.Column(db.String(100), nullable=False, index=True)
    area = db.Column(db.String(100), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    availability_status = db.Column(db.String(20), default='AVAILABLE') # 'AVAILABLE', 'UNAVAILABLE'
    verification_status = db.Column(db.String(20), default='UNVERIFIED') # 'UNVERIFIED', 'VERIFIED'
    last_donation_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    matches = db.relationship('DonorMatch', backref='donor_profile', cascade='all, delete-orphan')
    donations = db.relationship('Donation', backref='donor', cascade='all, delete-orphan')

    @property
    def is_available(self):
        return self.availability_status == 'AVAILABLE'

    @is_available.setter
    def is_available(self, value):
        if isinstance(value, bool):
            self.availability_status = 'AVAILABLE' if value else 'UNAVAILABLE'
        elif isinstance(value, str):
            self.availability_status = value.upper()

    @property
    def is_verified(self):
        return self.verification_status == 'VERIFIED'

    @property
    def lat(self):
        return round(self.latitude, 2) if self.latitude is not None else None

    @lat.setter
    def lat(self, val):
        self.latitude = val

    @property
    def lng(self):
        return round(self.longitude, 2) if self.longitude is not None else None

    @lng.setter
    def lng(self, val):
        self.longitude = val

    def to_dict(self, include_exact_location=False):
        lat = self.latitude
        lng = self.longitude
        if not include_exact_location and lat is not None and lng is not None:
            lat = round(lat, 2)
            lng = round(lng, 2)
        return {
            'id': self.id,
            'user_id': self.user_id,
            'blood_group': self.blood_group,
            'city': self.city,
            'area': self.area,
            'latitude': lat,
            'longitude': lng,
            'lat': lat,
            'lng': lng,
            'availability_status': self.availability_status,
            'is_available': self.is_available,
            'verification_status': self.verification_status,
            'is_verified': self.is_verified,
            'last_donation_date': self.last_donation_date.isoformat() if self.last_donation_date else None
        }
