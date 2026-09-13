from app import db
from datetime import datetime


class Media(db.Model):
    __tablename__ = "media"

    id = db.Column(db.Integer, primary_key=True)

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    file_path = db.Column(
        db.String(500),
        nullable=False
    )

    file_type = db.Column(
        db.String(50)
    )

    mime_type = db.Column(
        db.String(100)
    )

    file_size = db.Column(
        db.Integer
    )

    alt_text = db.Column(
        db.String(255)
    )

    title = db.Column(
        db.String(255)
    )

    caption = db.Column(
        db.Text
    )

    description = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
