# =========================================================
# RASBHAV BOOKS
# SEO MODEL
# =========================================================
#
# This model stores SEO data for:
#
#   • Books
#   • Authors
#   • Categories
#   • Pages
#   • Other CMS entities
#
# Main principle:
#
# ADMIN PANEL
#      ↓
# SEO DATABASE
#      ↓
# PUBLIC WEBSITE
#
# =========================================================

from datetime import datetime
import json

from app import db


class SEO(db.Model):
    __tablename__ = "seo_settings"

    # -----------------------------------------------------
    # PRIMARY KEY
    # -----------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # -----------------------------------------------------
    # ENTITY INFORMATION
    # -----------------------------------------------------
    #
    # Examples:
    #
    # entity_type = "book"
    # entity_id   = 10
    #
    # entity_type = "author"
    # entity_id   = 5
    #
    # entity_type = "category"
    # entity_id   = 3
    #
    # -----------------------------------------------------

    entity_type = db.Column(
        db.String(50),
        nullable=False,
        index=True
    )

    entity_id = db.Column(
        db.Integer,
        nullable=True,
        index=True
    )

    # -----------------------------------------------------
    # BASIC SEO
    # -----------------------------------------------------

    meta_title = db.Column(
        db.String(255)
    )

    meta_description = db.Column(
        db.Text
    )

    focus_keyword = db.Column(
        db.String(255)
    )

    # -----------------------------------------------------
    # CANONICAL & ROBOTS
    # -----------------------------------------------------

    canonical_url = db.Column(
        db.String(500)
    )

    robots = db.Column(
        db.String(100),
        default="index, follow",
        nullable=False
    )

    # -----------------------------------------------------
    # OPEN GRAPH
    # -----------------------------------------------------

    og_title = db.Column(
        db.String(255)
    )

    og_description = db.Column(
        db.Text
    )

    og_image = db.Column(
        db.String(500)
    )

    # -----------------------------------------------------
    # STRUCTURED DATA / JSON-LD
    # -----------------------------------------------------

    schema_data = db.Column(
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
    # JSON-LD METHODS
    # =====================================================

    def set_schema(self, data):
        """
        Store JSON-LD structured data safely.

        Accepts:
            dict
            list
            JSON string
        """

        if data is None:
            self.schema_data = None
            return

        if isinstance(data, (dict, list)):
            self.schema_data = json.dumps(
                data,
                ensure_ascii=False
            )
            return

        if isinstance(data, str):
            data = data.strip()

            if not data:
                self.schema_data = None
                return

            # Validate JSON before storing it.
            parsed = json.loads(data)

            self.schema_data = json.dumps(
                parsed,
                ensure_ascii=False
            )
            return

        raise ValueError(
            "schema_data must be a dict, list, JSON string, or None."
        )

    def get_schema(self):
        """
        Return schema_data as Python object.
        """

        if not self.schema_data:
            return None

        try:
            return json.loads(self.schema_data)
        except (TypeError, ValueError, json.JSONDecodeError):
            return None

    # =====================================================
    # SEO HELPER METHODS
    # =====================================================

    def get_meta_title(self, fallback=None):
        """
        Return SEO title or fallback title.
        """

        if self.meta_title:
            return self.meta_title.strip()

        return fallback

    def get_meta_description(self, fallback=None):
        """
        Return SEO description or fallback description.
        """

        if self.meta_description:
            return self.meta_description.strip()

        return fallback

    def get_robots(self):
        """
        Return robots directive.
        """

        return (
            self.robots.strip()
            if self.robots
            else "index, follow"
        )

    def has_open_graph(self):
        """
        Check whether Open Graph data exists.
        """

        return bool(
            self.og_title
            or self.og_description
            or self.og_image
        )

    def has_schema(self):
        """
        Check whether valid JSON-LD exists.
        """

        return self.get_schema() is not None

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return (
            f"<SEO "
            f"type={self.entity_type!r} "
            f"id={self.entity_id}>"
        )
