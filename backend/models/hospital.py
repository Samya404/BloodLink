from datetime import datetime, timezone
from extensions import db

class Hospital(db.Model):
    __tablename__ = 'hospitals'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=True, default='HOSPITAL') # 'HOSPITAL', 'BLOOD_BANK'
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=False, index=True)
    state = db.Column(db.String(100), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    verification_status = db.Column(db.String(20), default='UNVERIFIED') # 'UNVERIFIED', 'VERIFIED'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # User ID if the hospital has a manager account
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = db.relationship('User', backref=db.backref('hospital', uselist=False))

    # Relationships
    inventory = db.relationship('BloodInventory', backref='hospital', cascade='all, delete-orphan')
    requests = db.relationship('BloodRequest', backref='hospital_rel', cascade='all, delete-orphan')

    @property
    def is_verified(self):
        return self.verification_status == 'VERIFIED'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'hospital_name': self.name,
            'type': self.type,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'email': self.email,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'verification_status': self.verification_status,
            'is_verified': self.is_verified
        }
