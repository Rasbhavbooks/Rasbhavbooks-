# =========================================================
# RASBHAV BOOKS
# SITE SETTINGS MODEL
# =========================================================

from datetime import datetime
import json

from app import db


class SiteSetting(db.Model):
    __tablename__ = "site_settings"

    # -----------------------------------------------------
    # PRIMARY KEY
    # -----------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # -----------------------------------------------------
    # SETTING KEY
    # Example:
    # site_name
    # site_logo
    # favicon
    # contact_email
    # whatsapp_number
    # google_analytics
    # -----------------------------------------------------

    setting_key = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
        index=True
    )

    # -----------------------------------------------------
    # SETTING VALUE
    # -----------------------------------------------------

    setting_value = db.Column(
        db.Text,
        nullable=True
    )

    # -----------------------------------------------------
    # SETTING TYPE
    #
    # text
    # textarea
    # number
    # boolean
    # json
    # url
    # image
    # email
    # phone
    # -----------------------------------------------------

    setting_type = db.Column(
        db.String(50),
        default="text",
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
    # VALUE HELPERS
    # =====================================================

    def get_value(self, default=None):
        """
        Return raw setting value.
        """

        if self.setting_value is None:
            return default

        return self.setting_value

    # -----------------------------------------------------

    def set_value(self, value):
        """
        Save a normal value as string.
        """

        if value is None:
            self.setting_value = None
        else:
            self.setting_value = str(value)

    # -----------------------------------------------------

    def get_bool(self, default=False):
        """
        Convert setting value to boolean.
        """

        if self.setting_value is None:
            return default

        value = self.setting_value.strip().lower()

        if value in (
            "1",
            "true",
            "yes",
            "on",
            "enabled"
        ):
            return True

        if value in (
            "0",
            "false",
            "no",
            "off",
            "disabled"
        ):
            return False

        return default

    # -----------------------------------------------------

    def set_bool(self, value):
        """
        Save boolean value.
        """

        self.setting_value = (
            "true" if bool(value) else "false"
        )

    # -----------------------------------------------------

    def get_int(self, default=0):
        """
        Convert setting value to integer.
        """

        if self.setting_value is None:
            return default

        try:
            return int(self.setting_value)
        except (TypeError, ValueError):
            return default

    # -----------------------------------------------------

    def set_int(self, value):
        """
        Save integer value.
        """

        try:
            self.setting_value = str(int(value))
        except (TypeError, ValueError):
            raise ValueError(
                "Setting value must be an integer."
            )

    # -----------------------------------------------------

    def get_json(self, default=None):
        """
        Convert JSON string into Python object.
        """

        if not self.setting_value:
            return default

        try:
            return json.loads(self.setting_value)
        except (
            TypeError,
            ValueError,
            json.JSONDecodeError
        ):
            return default

    # -----------------------------------------------------

    def set_json(self, value):
        """
        Save dict/list as JSON.
        """

        if value is None:
            self.setting_value = None
            return

        if not isinstance(value, (dict, list)):
            raise ValueError(
                "JSON setting value must be a dict or list."
            )

        self.setting_value = json.dumps(
            value,
            ensure_ascii=False
        )

    # =====================================================
    # VALIDATION / HELPERS
    # =====================================================

    def is_empty(self):
        """
        Check whether setting has an empty value.
        """

        return not (
            self.setting_value
            and self.setting_value.strip()
        )

    # -----------------------------------------------------

    def has_value(self):
        """
        Check whether setting contains a value.
        """

        return not self.is_empty()

    # -----------------------------------------------------

    def get_clean_value(self, default=None):
        """
        Return trimmed string value.
        """

        if self.setting_value is None:
            return default

        value = self.setting_value.strip()

        if not value:
            return default

        return value

    # =====================================================
    # STATIC / CLASS HELPERS
    # =====================================================

    @classmethod
    def get(cls, key, default=None):
        """
        Get a setting directly by key.
        """

        if not key:
            return default

        setting = cls.query.filter_by(
            setting_key=key
        ).first()

        if not setting:
            return default

        return setting.get_value(default)

    # -----------------------------------------------------

    @classmethod
    def get_clean(cls, key, default=None):
        """
        Get trimmed setting value.
        """

        if not key:
            return default

        setting = cls.query.filter_by(
            setting_key=key
        ).first()

        if not setting:
            return default

        return setting.get_clean_value(default)

    # -----------------------------------------------------

    @classmethod
    def get_bool_value(cls, key, default=False):
        """
        Get boolean setting.
        """

        setting = cls.query.filter_by(
            setting_key=key
        ).first()

        if not setting:
            return default

        return setting.get_bool(default)

    # -----------------------------------------------------

    @classmethod
    def get_int_value(cls, key, default=0):
        """
        Get integer setting.
        """

        setting = cls.query.filter_by(
            setting_key=key
        ).first()

        if not setting:
            return default

        return setting.get_int(default)

    # -----------------------------------------------------

    @classmethod
    def get_json_value(cls, key, default=None):
        """
        Get JSON setting.
        """

        setting = cls.query.filter_by(
            setting_key=key
        ).first()

        if not setting:
            return default

        return setting.get_json(default)

    # -----------------------------------------------------

    @classmethod
    def set(cls, key, value, setting_type="text"):
        """
        Create or update a site setting.
        """

        if not key:
            raise ValueError(
                "Setting key cannot be empty."
            )

        key = str(key).strip()

        if not key:
            raise ValueError(
                "Setting key cannot be empty."
            )

        setting = cls.query.filter_by(
            setting_key=key
        ).first()

        if not setting:
            setting = cls(
                setting_key=key
            )

            db.session.add(setting)

        setting.setting_type = (
            str(setting_type).strip()
            if setting_type
            else "text"
        )

        setting.set_value(value)

        return setting

    # -----------------------------------------------------

    @classmethod
    def set_bool_value(cls, key, value):
        """
        Create or update a boolean setting.
        """

        setting = cls.query.filter_by(
            setting_key=key
        ).first()

        if not setting:
            setting = cls(
                setting_key=key
            )
            db.session.add(setting)

        setting.setting_type = "boolean"
        setting.set_bool(value)

        return setting

    # -----------------------------------------------------

    @classmethod
    def set_json_value(cls, key, value):
        """
        Create or update a JSON setting.
        """

        setting = cls.query.filter_by(
            setting_key=key
        ).first()

        if not setting:
            setting = cls(
                setting_key=key
            )
            db.session.add(setting)

        setting.setting_type = "json"
        setting.set_json(value)

        return setting

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return (
            f"<SiteSetting "
            f"{self.setting_key!r}="
            f"{self.setting_value!r}>"
        )
