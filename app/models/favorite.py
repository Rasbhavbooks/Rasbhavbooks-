# =========================================================
# RASBHAV BOOKS
# FAVORITE MODEL
# Flask-SQLAlchemy + SQLite
# =========================================================

from datetime import datetime

from app import db


class Favorite(db.Model):

    __tablename__ = "favorites"

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
            "favorites",
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
            "favorites",
            lazy="dynamic",
            cascade="all, delete-orphan",
            passive_deletes=True
        )
    )

    # =====================================================
    # TIMESTAMP
    # =====================================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    # =====================================================
    # UNIQUE CONSTRAINT
    # =====================================================
    #
    # One user can favorite a book only once.
    #
    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "book_id",
            name="uq_favorite_user_book"
        ),
    )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (
            f"<Favorite "
            f"user={self.user_id} "
            f"book={self.book_id}>"
        )
