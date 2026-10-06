from datetime import datetime, timezone
from extensions import db

class APISource(db.Model):
    __tablename__ = 'api_sources'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    source_type = db.Column(db.String(50), nullable=False) # e.g., 'ERAKTKOSH'
    enabled = db.Column(db.Boolean, default=True)
    last_successful_sync = db.Column(db.DateTime, nullable=True)
    last_error = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'source_type': self.source_type,
            'enabled': self.enabled,
            'last_successful_sync': self.last_successful_sync.isoformat() if self.last_successful_sync else None,
            'last_error': self.last_error,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
