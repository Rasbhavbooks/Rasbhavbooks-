# =========================================================
# RASBHAV BOOKS
# AUTHOR MODEL
# =========================================================

from datetime import datetime

from app import db


class Author(db.Model):
    __tablename__ = "authors"

    # -----------------------------------------------------
    # PRIMARY KEY
    # -----------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # -----------------------------------------------------
    # AUTHOR INFORMATION
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

    biography = db.Column(
        db.Text
    )

    profile_image = db.Column(
        db.String(500)
    )

    # -----------------------------------------------------
    # SOCIAL LINKS
    # -----------------------------------------------------
    #
    # Stored as JSON text.
    #
    # Example:
    #
    # {
    #     "website": "...",
    #     "instagram": "...",
    #     "facebook": "...",
    #     "youtube": "..."
    # }
    #
    # -----------------------------------------------------

    social_links = db.Column(
        db.Text
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

    def get_display_name(self):
        """
        Return a clean author name.
        """

        return (self.name or "").strip()

    def has_biography(self):
        """
        Check whether author biography exists.
        """

        return bool(
            self.biography and self.biography.strip()
        )

    def has_profile_image(self):
        """
        Check whether author has a profile image.
        """

        return bool(
            self.profile_image and self.profile_image.strip()
        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return f"<Author {self.name!r}>"
