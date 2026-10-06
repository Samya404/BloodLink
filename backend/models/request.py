from datetime import datetime, timezone
from extensions import db

class BloodRequest(db.Model):
    __tablename__ = 'blood_requests'

    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), nullable=True)
    patient_name = db.Column(db.String(150), nullable=True)
    hospital_name = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    blood_group = db.Column(db.String(5), nullable=False, index=True)
    component = db.Column(db.String(50), default='Whole Blood', nullable=True)
    units_required = db.Column(db.Integer, nullable=False, default=1)
    priority = db.Column(db.String(20), default='NORMAL') # 'NORMAL', 'URGENT', 'EMERGENCY'
    status = db.Column(db.String(20), default='PENDING', index=True) # 'PENDING', 'MATCHING', 'PARTIALLY_FULFILLED', 'FULFILLED', 'CANCELLED', 'EXPIRED'
    required_by = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    matches = db.relationship('DonorMatch', backref='blood_request', cascade='all, delete-orphan')

    @property
    def units(self):
        return self.units_required

    @units.setter
    def units(self, val):
        self.units_required = val

    @property
    def urgency_level(self):
        return self.priority

    @urgency_level.setter
    def urgency_level(self, val):
        self.priority = val

    def to_dict(self):
        return {
            'id': self.id,
            'requester_id': self.requester_id,
            'hospital_id': self.hospital_id,
            'patient_name': self.patient_name or (self.requester.full_name if self.requester else None),
            'hospital_name': self.hospital_name or (self.hospital_rel.name if self.hospital_rel else None),
            'city': self.city,
            'blood_group': self.blood_group,
            'component': self.component or 'Whole Blood',
            'units_required': self.units_required,
            'units': self.units_required,
            'priority': self.priority,
            'urgency_level': self.priority,
            'status': self.status,
            'required_by': self.required_by.isoformat() if self.required_by else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
