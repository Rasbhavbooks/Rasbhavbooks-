# =========================================================
# RASBHAV BOOKS
# READING PROGRESS MODEL
# Flask-SQLAlchemy + SQLite
# =========================================================

from datetime import datetime

from app import db


class ReadingProgress(db.Model):

    __tablename__ = "reading_progress"

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =====================================================
    # USER
    # =====================================================

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "reading_progress",
            lazy="dynamic",
            cascade="all, delete-orphan",
            passive_deletes=True
        )
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
            "reading_progress",
            lazy="dynamic",
            cascade="all, delete-orphan",
            passive_deletes=True
        )
    )

    # =====================================================
    # CHAPTER
    # =====================================================

    chapter_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "chapters.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    chapter = db.relationship(
        "Chapter",
        backref=db.backref(
            "reading_progress",
            lazy="dynamic",
            cascade="all, delete-orphan",
            passive_deletes=True
        )
    )

    # =====================================================
    # PROGRESS
    # =====================================================

    progress_percent = db.Column(
        db.Float,
        default=0,
        nullable=False
    )

    # =====================================================
    # LAST READING POSITION
    # =====================================================

    last_position = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    # =====================================================
    # LAST READ
    # =====================================================

    last_read_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        index=True
    )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (
            f"<ReadingProgress "
            f"user={self.user_id} "
            f"book={self.book_id} "
            f"chapter={self.chapter_id} "
            f"progress={self.progress_percent}>"
        )
