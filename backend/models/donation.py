from datetime import datetime, timezone
from extensions import db

class Donation(db.Model):
    __tablename__ = 'donations'

    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donor_profiles.id'), nullable=False)
    donation_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    blood_group = db.Column(db.String(5), nullable=False)
    component = db.Column(db.String(50), nullable=False)
    collection_location = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='COMPLETED')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'donor_id': self.donor_id,
            'donation_date': self.donation_date.isoformat() if self.donation_date else None,
            'blood_group': self.blood_group,
            'component': self.component,
            'collection_location': self.collection_location,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
