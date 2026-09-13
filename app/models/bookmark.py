from app import db
from datetime import datetime


class Bookmark(db.Model):
    __tablename__ = "bookmarks"

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

    position = db.Column(db.Integer, default=0)

    note = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
