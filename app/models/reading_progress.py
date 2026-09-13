from app import db
from datetime import datetime


class ReadingProgress(db.Model):
    __tablename__ = "reading_progress"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    book_id = db.Column(
        db.Integer,
        db.ForeignKey("books.id"),
        nullable=False
    )

    chapter_id = db.Column(
        db.Integer,
        db.ForeignKey("chapters.id"),
        nullable=False
    )

    progress_percent = db.Column(
        db.Float,
        default=0
    )

    last_position = db.Column(
        db.Integer,
        default=0
    )

    last_read_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
