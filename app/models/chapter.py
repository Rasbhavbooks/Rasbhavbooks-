from app import db
from datetime import datetime


class Chapter(db.Model):
    __tablename__ = "chapters"

    id = db.Column(db.Integer, primary_key=True)

    book_id = db.Column(
        db.Integer,
        db.ForeignKey("books.id"),
        nullable=False
    )

    chapter_number = db.Column(db.Integer, nullable=False)

    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)

    content = db.Column(db.Text, nullable=False)

    status = db.Column(
        db.String(20),
        default="draft"
    )

    publish_date = db.Column(db.DateTime)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
