# =========================================================
# RASBHAV BOOKS
# CATEGORY MODEL
# =========================================================

from datetime import datetime

from app import db


class Category(db.Model):
    __tablename__ = "categories"

    # -----------------------------------------------------
    # PRIMARY KEY
    # -----------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # -----------------------------------------------------
    # BASIC INFORMATION
    # -----------------------------------------------------

    name = db.Column(
        db.String(255),
        nullable=False,
        index=True
    )

    slug = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True
    )

    description = db.Column(
        db.Text
    )

    image = db.Column(
        db.String(500)
    )

    # -----------------------------------------------------
    # PARENT CATEGORY
    # -----------------------------------------------------
    #
    # Example:
    #
    # Fiction
    #   ├── Love Story
    #   ├── Sad Story
    #   └── Mystery
    #
    # -----------------------------------------------------

    parent_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "categories.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    parent = db.relationship(
        "Category",
        remote_side=[id],
        back_populates="children"
    )

    children = db.relationship(
        "Category",
        back_populates="parent",
        cascade="all, delete-orphan",
        single_parent=True
    )

    # -----------------------------------------------------
    # TIMESTAMPS
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
    # HELPER METHODS
    # =====================================================

    def get_full_name(self):
        """
        Return category name with parent hierarchy.

        Example:
        Fiction → Love Story
        """

        if self.parent:
            return f"{self.parent.name} → {self.name}"

        return self.name

    def is_parent(self):
        """
        Check whether this category has child categories.
        """

        return len(self.children) > 0

    def has_parent(self):
        """
        Check whether this category belongs to another category.
        """

        return self.parent_id is not None

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return f"<Category {self.name!r}>"
