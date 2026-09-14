# =========================================================
# RASBHAV BOOKS
# USER MODEL
# Flask-SQLAlchemy + SQLite
# =========================================================

from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(db.Model):

    __tablename__ = "users"

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =====================================================
    # USERNAME
    # =====================================================

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
        index=True
    )

    # =====================================================
    # EMAIL
    # =====================================================

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True
    )

    # =====================================================
    # PASSWORD
    # =====================================================

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    # =====================================================
    # PROFILE
    # =====================================================

    full_name = db.Column(
        db.String(255)
    )

    # =====================================================
    # ACCOUNT STATUS
    # =====================================================

    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
        index=True
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
    # PASSWORD HELPERS
    # =====================================================

    def set_password(self, password):

        self.password_hash = generate_password_hash(
            password
        )

    def check_password(self, password):

        if not self.password_hash:
            return False

        return check_password_hash(
            self.password_hash,
            password
        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (
            f"<User "
            f"{self.username!r}>"
        )
