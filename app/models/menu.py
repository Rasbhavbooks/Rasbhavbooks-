# =========================================================
# RASBHAV BOOKS
# MENU MODEL
# =========================================================

from datetime import datetime

from app import db


class Menu(db.Model):
    __tablename__ = "menus"

    # -----------------------------------------------------
    # PRIMARY KEY
    # -----------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # -----------------------------------------------------
    # MENU NAME
    #
    # Examples:
    # Main Menu
    # Footer Menu
    # Mobile Menu
    # -----------------------------------------------------

    name = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )

    # -----------------------------------------------------
    # MENU LOCATION
    #
    # Examples:
    # header
    # footer
    # mobile
    # sidebar
    # custom
    # -----------------------------------------------------

    location = db.Column(
        db.String(50),
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
    # DESCRIPTION
    # -----------------------------------------------------

    description = db.Column(
        db.Text,
        nullable=True
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

    def get_name(self):
        return (
            self.name.strip()
            if self.name
            else ""
        )

    # -----------------------------------------------------

    def get_location(self):
        return (
            self.location.strip()
            if self.location
            else ""
        )

    # -----------------------------------------------------

    def has_description(self):
        return bool(
            self.description
            and self.description.strip()
        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return (
            f"<Menu "
            f"{self.name!r} "
            f"location={self.location!r}>"
        )
