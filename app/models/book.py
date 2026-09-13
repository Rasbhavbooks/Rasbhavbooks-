from app import db
from datetime import datetime


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)

    subtitle = db.Column(db.String(255))
    description = db.Column(db.Text)
    short_description = db.Column(db.Text)

    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"))
    language = db.Column(db.String(50))

    tags = db.Column(db.Text)

    cover_image = db.Column(db.String(500))
    banner_image = db.Column(db.String(500))
    featured_image = db.Column(db.String(500))

    status = db.Column(db.String(20), default="draft")
    featured = db.Column(db.Boolean, default=False)
    published = db.Column(db.Boolean, default=False)

    publish_date = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
