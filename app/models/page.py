from app import db
from datetime import datetime


class Page(db.Model):
    __tablename__ = "pages"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)

    content = db.Column(db.Text)

    featured_image = db.Column(db.String(500))

    status = db.Column(
        db.String(20),
        default="draft"
    )

    template = db.Column(
        db.String(100),
        default="default"
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
