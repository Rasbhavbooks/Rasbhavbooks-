# =========================================================
# RASBHAV BOOKS
# BOOKMARK MODEL
# Flask-SQLAlchemy + SQLite
# =========================================================

from datetime import datetime

from app import db


class Bookmark(db.Model):

    __tablename__ = "bookmarks"

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
            "bookmarks",
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
            "bookmarks",
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
            "bookmarks",
            lazy="dynamic",
            cascade="all, delete-orphan",
            passive_deletes=True
        )
    )

    # =====================================================
    # READING POSITION
    # =====================================================

    position = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    # =====================================================
    # NOTE
    # =====================================================

    note = db.Column(
        db.Text
    )

    # =====================================================
    # TIMESTAMP
    # =====================================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (
            f"<Bookmark "
            f"user={self.user_id} "
            f"book={self.book_id} "
            f"chapter={self.chapter_id}>"
        )
