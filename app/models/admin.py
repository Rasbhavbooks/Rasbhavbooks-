# =========================================================
# RASBHAV BOOKS
# ADMIN MODEL
# =========================================================

from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class Admin(db.Model):
    __tablename__ = "admins"

    # -----------------------------------------------------
    # PRIMARY KEY
    # -----------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # -----------------------------------------------------
    # LOGIN INFORMATION
    # -----------------------------------------------------

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
        index=True
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    # -----------------------------------------------------
    # PROFILE
    # -----------------------------------------------------

    full_name = db.Column(
        db.String(255)
    )

    # -----------------------------------------------------
    # ACCOUNT STATUS
    # -----------------------------------------------------

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
        index=True
    )

    is_super_admin = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        index=True
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
    # PASSWORD METHODS
    # =====================================================

    def set_password(self, password):
        """
        Hash and store admin password.
        """

        if not password:
            raise ValueError("Password cannot be empty.")

        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verify admin password.
        """

        if not password or not self.password_hash:
            return False

        try:
            return check_password_hash(
                self.password_hash,
                password
            )
        except Exception:
            return False

    # =====================================================
    # HELPER METHODS
    # =====================================================

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def make_super_admin(self):
        self.is_super_admin = True

    def remove_super_admin(self):
        self.is_super_admin = False

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return f"<Admin {self.username!r}>"
