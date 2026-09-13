from app import db
from datetime import datetime


class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)

    menu_id = db.Column(
        db.Integer,
        db.ForeignKey("menus.id"),
        nullable=False
    )

    name = db.Column(db.String(255), nullable=False)

    item_type = db.Column(
        db.String(50),
        default="custom_url"
    )

    url = db.Column(db.String(500))

    page_id = db.Column(
        db.Integer,
        db.ForeignKey("pages.id")
    )

    book_id = db.Column(
        db.Integer,
        db.ForeignKey("books.id")
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id")
    )

    open_new_tab = db.Column(
        db.Boolean,
        default=False
    )

    position = db.Column(
        db.Integer,
        default=0
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
