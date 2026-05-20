import uuid
from datetime import datetime, timezone
from app.extensions import db


class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'))
    status_id = db.Column(db.Integer, db.ForeignKey('statuses.id', ondelete='SET NULL'))
    latitude = db.Column(db.Numeric(10, 7), nullable=False)
    longitude = db.Column(db.Numeric(10, 7), nullable=False)
    address = db.Column(db.String(255))
    photo_url = db.Column(db.String(512))
    ai_priority_suggestion = db.Column(db.String(50))
    ai_category_confidence = db.Column(db.Numeric(5, 2))
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    is_deleted = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Ticket {self.id}>'
