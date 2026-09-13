from app import db
from datetime import datetime


class Widget(db.Model):
    __tablename__ = "widgets"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(255),
        nullable=False
    )

    widget_type = db.Column(
        db.String(100),
        nullable=False
    )

    title = db.Column(
        db.String(255)
    )

    content = db.Column(
        db.Text
    )

    settings = db.Column(
        db.Text
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    position = db.Column(
        db.Integer,
        default=0
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
