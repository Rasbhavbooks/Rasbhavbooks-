# =========================================================
# RASBHAV BOOKS
# LAYOUT SECTION MODEL
# =========================================================

from datetime import datetime
import json

from app import db


class LayoutSection(db.Model):
    __tablename__ = "layout_sections"

    id = db.Column(db.Integer, primary_key=True)

    # =====================================================
    # SECTION IDENTITY
    # =====================================================

    section_key = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )

    section_type = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )

    # =====================================================
    # SECTION CONTENT
    # =====================================================

    title = db.Column(
        db.String(255),
        nullable=True
    )

    subtitle = db.Column(
        db.Text,
        nullable=True
    )

    content = db.Column(
        db.Text,
        nullable=True
    )

    # =====================================================
    # PAGE / LOCATION
    # =====================================================

    page_slug = db.Column(
        db.String(255),
        nullable=False,
        default="home",
        index=True
    )

    # =====================================================
    # DYNAMIC SETTINGS
    # =====================================================

    settings = db.Column(
        db.Text,
        nullable=True
    )

    # =====================================================
    # DISPLAY CONTROL
    # =====================================================

    position = db.Column(
        db.Integer,
        default=0,
        nullable=False,
        index=True
    )

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
    # STATUS
    # =====================================================

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def is_enabled(self):
        return bool(self.is_active)

    # =====================================================
    # BASIC HELPERS
    # =====================================================

    def get_key(self):
        return (
            self.section_key.strip()
            if self.section_key
            else ""
        )

    def get_type(self):
        return (
            self.section_type.strip()
            if self.section_type
            else ""
        )

    def get_page_slug(self):
        return (
            self.page_slug.strip()
            if self.page_slug
            else "home"
        )

    def get_title(self, fallback=None):
        if self.title:
            return self.title.strip()

        return fallback

    def get_subtitle(self, fallback=None):
        if self.subtitle:
            return self.subtitle.strip()

        return fallback

    def get_content(self, fallback=None):
        if self.content:
            return self.content

        return fallback

    def has_title(self):
        return bool(
            self.title and self.title.strip()
        )

    def has_subtitle(self):
        return bool(
            self.subtitle and self.subtitle.strip()
        )

    def has_content(self):
        return bool(
            self.content and self.content.strip()
        )

    # =====================================================
    # SETTINGS JSON
    # =====================================================

    def get_settings(self, default=None):
        if not self.settings:
            return default

        try:
            return json.loads(self.settings)

        except (
            TypeError,
            ValueError,
            json.JSONDecodeError
        ):
            return default

    def set_settings(self, value):
        if value is None:
            self.settings = None
            return

        if not isinstance(value, (dict, list)):
            raise ValueError(
               
