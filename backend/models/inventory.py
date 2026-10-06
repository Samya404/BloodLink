from datetime import datetime, timezone
from extensions import db

class BloodInventory(db.Model):
    __tablename__ = 'blood_inventory'

    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), nullable=False, index=True)
    blood_group = db.Column(db.String(5), nullable=False, index=True)
    component = db.Column(db.String(50), nullable=False, default='Whole Blood') # 'Whole Blood', 'Packed Red Blood Cells', 'Plasma', 'Platelets'
    available_units = db.Column(db.Integer, default=0)
    reserved_units = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    source_type = db.Column(db.String(20), default='LOCAL') # 'LOCAL', 'EXTERNAL', 'DEMO'
    
    __table_args__ = (db.UniqueConstraint('hospital_id', 'blood_group', 'component', name='_hospital_bg_comp_uc'),)

    @property
    def units(self):
        return self.available_units
        
    @units.setter
    def units(self, val):
        self.available_units = val

    @property
    def updated_at(self):
        return self.last_updated

    def to_dict(self):
        return {
            'id': self.id,
            'hospital_id': self.hospital_id,
            'hospital_name': self.hospital.name if self.hospital else None,
            'blood_group': self.blood_group,
            'component': self.component,
            'available_units': self.available_units,
            'units': self.available_units,
            'reserved_units': self.reserved_units,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'updated_at': self.last_updated.isoformat() if self.last_updated else None,
            'source_type': self.source_type
        }
