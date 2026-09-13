from app import db
from datetime import datetime


class SiteSetting(db.Model):
    __tablename__ = "site_settings"

    id = db.Column(db.Integer, primary_key=True)

    setting_key = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    setting_value = db.Column(db.Text)

    setting_type = db.Column(
        db.String(50),
        default="text"
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
