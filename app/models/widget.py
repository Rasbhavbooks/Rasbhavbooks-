# =========================================================
# RASBHAV BOOKS
# WIDGET MODEL
# =========================================================

from datetime import datetime
import json

from app import db


class Widget(db.Model):
    __tablename__ = "widgets"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(255),
        nullable=False,
        index=True
    )

    widget_type = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )

    title = db.Column(
        db.String(255),
        nullable=True
    )

    content = db.Column(
        db.Text,
        nullable=True
    )

    settings = db.Column(
        db.Text,
        nullable=True
    )

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

    def get_name(self):
        return self.name.strip() if self.name else ""

    def get_type(self):
        return (
            self.widget_type.strip()
            if self.widget_type
            else ""
        )

    def get_title(self, fallback=None):
        if self.title:
            return self.title.strip()

        return fallback

    def get_content(self, fallback=None):
        if self.content:
            return self.content

        return fallback

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
                "Widget settings must be a dict, list, or None."
            )

        self.settings = json.dumps(
            value,
            ensure_ascii=False
        )

    # =====================================================
    # SETTINGS HELPERS
    # =====================================================

    def get_setting(self, key, default=None):
        settings = self.get_settings({})

        if not isinstance(settings, dict):
            return default

        return settings.get(key, default)

    def set_setting(self, key, value):
        if not key:
            raise ValueError(
                "Widget setting key cannot be empty."
            )

        settings = self.get_settings({})

        if not isinstance(settings, dict):
            settings = {}

        settings[str(key).strip()] = value

        self.set_settings(settings)

    def has_setting(self, key):
        settings = self.get_settings({})

        return (
            isinstance(settings, dict)
            and key in settings
        )

    # =====================================================
    # POSITION
    # =====================================================

    def get_position(self):
        return self.position if self.position is not None else 0

    def set_position(self, position):
        try:
            self.position = int(position)

        except (TypeError, ValueError):
            raise ValueError(
                "Widget position must be an integer."
            )

    # =====================================================
    # CLASS METHODS
    # =====================================================

    @classmethod
    def get_active(cls):
        return (
            cls.query
            .filter_by(is_active=True)
            .order_by(cls.position.asc(), cls.id.asc())
            .all()
        )

    @classmethod
    def get_by_type(cls, widget_type):
        if not widget_type:
            return []

        return (
            cls.query
            .filter_by(
                widget_type=str(widget_type).strip(),
                is_active=True
            )
            .order_by(cls.position.asc(), cls.id.asc())
            .all()
        )

    @classmethod
    def get_by_name(cls, name):
        if not name:
            return None

        return (
            cls.query
            .filter_by(name=str(name).strip())
            .first()
        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return (
            f"<Widget "
            f"{self.name!r} "
            f"type={self.widget_type!r}>"
        )
