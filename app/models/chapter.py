# =========================================================
# RASBHAV BOOKS
# CHAPTER MODEL
# Flask-SQLAlchemy + SQLite
# =========================================================

from datetime import datetime

from app import db


class Chapter(db.Model):

    __tablename__ = "chapters"

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =====================================================
    # BOOK
    # =====================================================

    book_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "books.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    book = db.relationship(
        "Book",
        backref=db.backref(
            "chapters",
            lazy="dynamic",
            cascade="all, delete-orphan",
            passive_deletes=True
        )
    )

    # =====================================================
    # CHAPTER INFORMATION
    # =====================================================

    chapter_number = db.Column(
        db.Integer,
        nullable=False
    )

    title = db.Column(
        db.String(255),
        nullable=False
    )

    slug = db.Column(
        db.String(255),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    # =====================================================
    # STATUS
    # =====================================================

    status = db.Column(
        db.String(20),
        default="draft",
        nullable=False
    )

    published = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True
    )

    publish_date = db.Column(
        db.DateTime
    )

    # =====================================================
    # TIMESTAMPS
    # =====================================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (
            f"<Chapter "
            f"{self.chapter_number}: "
            f"{self.title!r}>"
        )
