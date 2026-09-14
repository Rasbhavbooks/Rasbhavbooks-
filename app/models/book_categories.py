# =========================================================
# RASBHAV BOOKS
# BOOK ↔ CATEGORY RELATIONSHIP MODEL
# =========================================================

from app import db


class BookCategory(db.Model):
    __tablename__ = "book_categories"

    # -----------------------------------------------------
    # PRIMARY KEY
    # -----------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # -----------------------------------------------------
    # BOOK
    # -----------------------------------------------------

    book_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "books.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # -----------------------------------------------------
    # CATEGORY
    # -----------------------------------------------------

    category_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "categories.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # -----------------------------------------------------
    # PREVENT DUPLICATE RELATIONSHIPS
    # -----------------------------------------------------

    __table_args__ = (
        db.UniqueConstraint(
            "book_id",
            "category_id",
            name="unique_book_category"
        ),
    )

    # -----------------------------------------------------
    # REPRESENTATION
    # -----------------------------------------------------

    def __repr__(self):
        return (
            f"<BookCategory "
            f"book={self.book_id} "
            f"category={self.category_id}>"
        )
