from app import db
from datetime import datetime

from app.models.book_categories import BookCategory


class Book(db.Model):
    __tablename__ = "books"

    # =========================================================
    # PRIMARY KEY
    # =========================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =========================================================
    # BASIC BOOK INFORMATION
    # =========================================================

    title = db.Column(
        db.String(255),
        nullable=False
    )

    slug = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )

    subtitle = db.Column(
        db.String(255)
    )

    description = db.Column(
        db.Text
    )

    short_description = db.Column(
        db.Text
    )

    # =========================================================
    # AUTHOR
    # =========================================================

    author_id = db.Column(
        db.Integer,
        db.ForeignKey("authors.id")
    )

    author = db.relationship(
        "Author",
        backref=db.backref(
            "books",
            lazy=True
        )
    )

    # =========================================================
    # LANGUAGE
    # =========================================================

    language = db.Column(
        db.String(50)
    )

    # =========================================================
    # TAGS
    # =========================================================

    tags = db.Column(
        db.Text
    )

    # =========================================================
    # IMAGES
    # =========================================================

    cover_image = db.Column(
        db.String(500)
    )

    banner_image = db.Column(
        db.String(500)
    )

    featured_image = db.Column(
        db.String(500)
    )

    # =========================================================
    # STATUS
    # =========================================================

    status = db.Column(
        db.String(20),
        default="draft"
    )

    featured = db.Column(
        db.Boolean,
        default=False
    )

    published = db.Column(
        db.Boolean,
        default=False
    )

    publish_date = db.Column(
        db.DateTime
    )

    # =========================================================
    # CATEGORIES
    # =========================================================
    #
    # book_categories.py association model:
    #
    # book_id
    # category_id
    #
    # This relationship allows:
    #
    # book.categories
    #
    # =========================================================

    categories = db.relationship(
        "Category",
        secondary=BookCategory.__table__,
        primaryjoin=(
            id == BookCategory.book_id
        ),
        secondaryjoin=(
            "Category.id == book_categories.c.category_id"
        ),
        backref=db.backref(
            "books",
            lazy="dynamic"
        ),
        lazy="select"
    )

    # =========================================================
    # TIMESTAMPS
    # =========================================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # =========================================================
    # REPRESENTATION
    # =========================================================

    def __repr__(self):
        return (
            f"<Book {self.title!r}>"
        )
