from app import db
from datetime import datetime


class SEO(db.Model):
    __tablename__ = "seo_settings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    entity_type = db.Column(
        db.String(50),
        nullable=False
    )

    entity_id = db.Column(
        db.Integer
    )

    meta_title = db.Column(
        db.String(255)
    )

    meta_description = db.Column(
        db.Text
    )

    focus_keyword = db.Column(
        db.String(255)
    )

    canonical_url = db.Column(
        db.String(500)
    )

    robots = db.Column(
        db.String(100),
        default="index, follow"
    )

    og_title = db.Column(
        db.String(255)
    )

    og_description = db.Column(
        db.Text
    )

    og_image = db.Column(
        db.String(500)
    )

    schema_data = db.Column(
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
