from app import db


class BookCategory(db.Model):
    __tablename__ = "book_categories"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    book_id = db.Column(
        db.Integer,
        db.ForeignKey("books.id"),
        nullable=False
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint(
            "book_id",
            "category_id",
            name="unique_book_category"
        ),
    )
