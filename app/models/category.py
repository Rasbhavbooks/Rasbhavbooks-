# =========================================================
# RASBHAV BOOKS
# CATEGORY MODEL
# =========================================================
#
# Category System
#
# CATEGORY
#   ↓
# Parent / Child Hierarchy
#   ↓
# Books Mapping
#   ↓
# Public Website
#
# Features:
# - Category CRUD support
# - Unique slug
# - Parent / Child categories
# - Safe hierarchy
# - Database SET NULL on parent delete
# - No accidental child deletion
# - Timestamps
# - Helper methods
# =========================================================


from datetime import datetime

from app import db


class Category(db.Model):
    __tablename__ = "categories"


    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    # =====================================================
    # BASIC INFORMATION
    # =====================================================

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


    # =====================================================
    # PARENT CATEGORY
    # =====================================================
    #
    # Example:
    #
    # Fiction
    #   ├── Love Story
    #   ├── Sad Story
    #   └── Mystery
    #
    # If Fiction is deleted:
    #
    # Love Story → Root
    # Sad Story  → Root
    # Mystery    → Root
    #
    # Child categories are NOT deleted.
    #
    # =====================================================

    parent_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "categories.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )


    # =====================================================
    # PARENT RELATIONSHIP
    # =====================================================

    parent = db.relationship(
        "Category",
        remote_side=[id],
        back_populates="children"
    )


    # =====================================================
    # CHILDREN RELATIONSHIP
    # =====================================================
    #
    # IMPORTANT:
    #
    # Do NOT use:
    #
    # cascade="all, delete-orphan"
    #
    # here.
    #
    # Because deleting a parent category must NOT delete
    # its child categories.
    #
    # Database FK uses:
    #
    # ON DELETE SET NULL
    #
    # Therefore children safely become root categories.
    #
    # =====================================================

    children = db.relationship(
        "Category",
        back_populates="parent",
        cascade="save-update, merge",
        passive_deletes=True
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
    # HELPER METHODS
    # =====================================================

    def get_full_name(self):
        """
        Return category name with parent hierarchy.

        Example:

        Fiction → Love Story
        """

        if self.parent:

            return (
                f"{self.parent.name} → {self.name}"
            )

        return self.name


    # =====================================================
    # IS PARENT
    # =====================================================

    def is_parent(self):
        """
        Return True if this category has children.
        """

        return bool(
            self.children
        )


    # =====================================================
    # HAS PARENT
    # =====================================================

    def has_parent(self):
        """
        Return True if this category belongs to
        another category.
        """

        return self.parent_id is not None


    # =====================================================
    # ROOT CATEGORY
    # =====================================================

    def is_root(self):
        """
        Return True if this category has no parent.
        """

        return self.parent_id is None


    # =====================================================
    # CHILD COUNT
    # =====================================================

    def child_count(self):
        """
        Return number of direct child categories.
        """

        return len(
            self.children
        )


    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (
            f"<Category {self.name!r}>"
        )
