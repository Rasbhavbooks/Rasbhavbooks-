# =========================================================
# RASBHAV BOOKS
# MENU ITEM MODEL
# =========================================================

from datetime import datetime

from app import db


class MenuItem(db.Model):
    __tablename__ = "menu_items"

    # -----------------------------------------------------
    # PRIMARY KEY
    # -----------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # -----------------------------------------------------
    # MENU
    # -----------------------------------------------------

    menu_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "menus.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    menu = db.relationship(
        "Menu",
        backref=db.backref(
            "items",
            lazy="dynamic",
            cascade="all, delete-orphan",
            passive_deletes=True
        )
    )

    # -----------------------------------------------------
    # ITEM NAME
    # -----------------------------------------------------

    name = db.Column(
        db.String(255),
        nullable=False,
        index=True
    )

    # -----------------------------------------------------
    # ITEM TYPE
    #
    # custom_url
    # page
    # book
    # category
    # author
    # home
    # books
    # search
    # -----------------------------------------------------

    item_type = db.Column(
        db.String(50),
        default="custom_url",
        nullable=False,
        index=True
    )

    # -----------------------------------------------------
    # CUSTOM URL
    # -----------------------------------------------------

    url = db.Column(
        db.String(500),
        nullable=True
    )

    # -----------------------------------------------------
    # PAGE LINK
    # -----------------------------------------------------

    page_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "pages.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    page = db.relationship(
        "Page",
        backref=db.backref(
            "menu_items",
            lazy="dynamic"
        )
    )

    # -----------------------------------------------------
    # BOOK LINK
    # -----------------------------------------------------

    book_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "books.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    book = db.relationship(
        "Book",
        backref=db.backref(
            "menu_items",
            lazy="dynamic"
        )
    )

    # -----------------------------------------------------
    # CATEGORY LINK
    # -----------------------------------------------------

    category_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "categories.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    category = db.relationship(
        "Category",
        backref=db.backref(
            "menu_items",
            lazy="dynamic"
        )
    )

    # -----------------------------------------------------
    # OPEN IN NEW TAB
    # -----------------------------------------------------

    open_new_tab = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    # -----------------------------------------------------
    # SORT POSITION
    # -----------------------------------------------------

    position = db.Column(
        db.Integer,
        default=0,
        nullable=False,
        index=True
    )

    # -----------------------------------------------------
    # ACTIVE / INACTIVE
    # -----------------------------------------------------

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
        index=True
    )

    # -----------------------------------------------------
    # CREATED / UPDATED
    # -----------------------------------------------------

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
    # HELPERS
    # =====================================================

    def activate(self):
        self.is_active = True

    # -----------------------------------------------------

    def deactivate(self):
        self.is_active = False

    # -----------------------------------------------------

    def is_enabled(self):
        return bool(self.is_active)

    # -----------------------------------------------------

    def should_open_new_tab(self):
        return bool(self.open_new_tab)

    # -----------------------------------------------------

    def get_name(self):
        return (
            self.name.strip()
            if self.name
            else ""
        )

    # -----------------------------------------------------

    def get_url(self):
        return (
            self.url.strip()
            if self.url
            else None
        )

    # -----------------------------------------------------

    def get_item_type(self):
        return (
            self.item_type.strip()
            if self.item_type
            else "custom_url"
        )

    # =====================================================
    # TARGET HELPERS
    # =====================================================

    def has_page_target(self):
        return self.page_id is not None

    # -----------------------------------------------------

    def has_book_target(self):
        return self.book_id is not None

    # -----------------------------------------------------

    def has_category_target(self):
        return self.category_id is not None

    # -----------------------------------------------------

    def has_custom_url(self):
        return bool(
            self.url
            and self.url.strip()
        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return (
            f"<MenuItem "
            f"{self.name!r} "
            f"menu={self.menu_id} "
            f"position={self.position}>"
        )
