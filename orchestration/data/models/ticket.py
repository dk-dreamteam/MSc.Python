import uuid
from datetime import datetime


class Ticket:
    def __init__(
        self,
        id: uuid.UUID | None = None,
        title: str | None = None,
        description: str | None = None,
        category_id: int | None = None,
        status_id: int | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        address: str | None = None,
        photo_url: str | None = None,
        ai_priority_suggestion: str | None = None,
        ai_category_confidence: float | None = None,
        admin_notes: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        is_deleted: bool = False,
        status_name: str | None = None,
        category_name: str | None = None,
    ):
        self.id = id
        self.title = title
        self.description = description
        self.category_id = category_id
        self.status_id = status_id
        self.latitude = latitude
        self.longitude = longitude
        self.address = address
        self.photo_url = photo_url
        self.ai_priority_suggestion = ai_priority_suggestion
        self.ai_category_confidence = ai_category_confidence
        self.admin_notes = admin_notes
        self.created_at = created_at
        self.updated_at = updated_at
        self.is_deleted = is_deleted
        self.status_name = status_name
        self.category_name = category_name

    def to_dict(self) -> dict:
        return {
            "id": str(self.id) if self.id else None,
            "title": self.title,
            "description": self.description,
            "category_id": self.category_id,
            "status_id": self.status_id,
            "latitude": float(self.latitude) if self.latitude is not None else None,
            "longitude": float(self.longitude) if self.longitude is not None else None,
            "address": self.address,
            "photo_url": self.photo_url,
            "ai_priority_suggestion": self.ai_priority_suggestion,
            "ai_category_confidence": float(self.ai_category_confidence) if self.ai_category_confidence is not None else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "status_name": self.status_name,
            "category_name": self.category_name,
        }
