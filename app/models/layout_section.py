from app import db
from datetime import datetime


class LayoutSection(db.Model):
    __tablename__ = "layout_sections"

    id = db.Column(db.Integer, primary_key=True)

    section_key = db.Column(
        db.String(100),
        nullable=False
    )

    section_type = db.Column(
        db.String(100),
        nullable=False
    )

    title = db.Column(
        db.String(255)
    )

    subtitle = db.Column(
        db.Text
    )

    content = db.Column(
        db.Text
    )

    settings = db.Column(
        db.Text
    )

    position = db.Column(
        db.Integer,
        default=0
    )

    is_active = db.Column(
        db.Boolean,
        default=True
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
