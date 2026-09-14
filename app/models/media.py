# =========================================================
# RASBHAV BOOKS
# MEDIA MODEL
# =========================================================

from datetime import datetime

from app import db


class Media(db.Model):
    __tablename__ = "media"

    # -----------------------------------------------------
    # PRIMARY KEY
    # -----------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # -----------------------------------------------------
    # FILE INFORMATION
    # -----------------------------------------------------

    filename = db.Column(
        db.String(255),
        nullable=False,
        index=True
    )

    file_path = db.Column(
        db.String(500),
        nullable=False
    )

    file_type = db.Column(
        db.String(50),
        nullable=True,
        index=True
    )

    mime_type = db.Column(
        db.String(100),
        nullable=True,
        index=True
    )

    file_size = db.Column(
        db.Integer,
        nullable=True
    )

    # -----------------------------------------------------
    # MEDIA URL
    # -----------------------------------------------------

    url = db.Column(
        db.String(1000),
        nullable=True
    )

    # -----------------------------------------------------
    # IMAGE SEO
    # -----------------------------------------------------

    alt_text = db.Column(
        db.String(255),
        nullable=True
    )

    title = db.Column(
        db.String(255),
        nullable=True
    )

    caption = db.Column(
        db.Text,
        nullable=True
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    # -----------------------------------------------------
    # IMAGE DIMENSIONS
    # -----------------------------------------------------

    width = db.Column(
        db.Integer,
        nullable=True
    )

    height = db.Column(
        db.Integer,
        nullable=True
    )

    # -----------------------------------------------------
    # UPLOAD INFORMATION
    # -----------------------------------------------------

    uploaded_by = db.Column(
        db.Integer,
        db.ForeignKey(
            "admins.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    uploader = db.relationship(
        "Admin",
        backref=db.backref(
            "media_files",
            lazy="dynamic"
        )
    )

    # -----------------------------------------------------
    # CREATED / UPDATED
    # -----------------------------------------------------

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # =====================================================
    # FILE HELPERS
    # =====================================================

    def get_filename(self):
        return (
            self.filename.strip()
            if self.filename
            else ""
        )

    # -----------------------------------------------------

    def get_file_path(self):
        return (
            self.file_path.strip()
            if self.file_path
            else ""
        )

    # -----------------------------------------------------

    def get_url(self):
        if self.url:
            return self.url.strip()

        return self.get_file_path()

    # -----------------------------------------------------

    def get_file_type(self):
        return (
            self.file_type.strip().lower()
            if self.file_type
            else ""
        )

    # -----------------------------------------------------

    def get_mime_type(self):
        return (
            self.mime_type.strip().lower()
            if self.mime_type
            else ""
        )

    # =====================================================
    # IMAGE HELPERS
    # =====================================================

    def is_image(self):
        """
        Check whether this media file is an image.
        """

        if self.file_type:
            return self.file_type.lower() in (
                "image",
                "jpg",
                "jpeg",
                "png",
                "webp",
                "gif",
                "svg"
            )

        if self.mime_type:
            return self.mime_type.lower().startswith(
                "image/"
            )

        return False

    # -----------------------------------------------------

    def has_dimensions(self):
        return (
            self.width is not None
            and self.height is not None
        )

    # -----------------------------------------------------

    def get_dimensions(self):
        if not self.has_dimensions():
            return None

        return {
            "width": self.width,
            "height": self.height
        }

    # =====================================================
    # SEO HELPERS
    # =====================================================

    def get_alt_text(self, fallback=None):
        if self.alt_text:
            return self.alt_text.strip()

        return fallback

    # -----------------------------------------------------

    def get_title(self, fallback=None):
        if self.title:
            return self.title.strip()

        return fallback

    # -----------------------------------------------------

    def has_caption(self):
        return bool(
            self.caption
            and self.caption.strip()
        )

    # -----------------------------------------------------

    def has_description(self):
        return bool(
            self.description
            and self.description.strip()
        )

    # =====================================================
    # FILE SIZE HELPERS
    # =====================================================

    def get_file_size_kb(self):
        if self.file_size is None:
            return 0

        return round(
            self.file_size / 1024,
            2
        )

    # -----------------------------------------------------

    def get_file_size_mb(self):
        if self.file_size is None:
            return 0

        return round(
            self.file_size / (1024 * 1024),
            2
        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return (
            f"<Media "
            f"{self.filename!r}>"
        )
