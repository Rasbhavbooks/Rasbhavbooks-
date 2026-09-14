# =========================================================
# RASBHAV BOOKS
# PAGE MODEL
# =========================================================

from datetime import datetime

from app import db


class Page(db.Model):
    __tablename__ = "pages"

    # -----------------------------------------------------
    # PRIMARY KEY
    # -----------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # -----------------------------------------------------
    # BASIC PAGE INFORMATION
    # -----------------------------------------------------

    title = db.Column(
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

    # -----------------------------------------------------
    # PAGE CONTENT
    # -----------------------------------------------------

    content = db.Column(
        db.Text,
        nullable=True
    )

    # -----------------------------------------------------
    # FEATURED IMAGE
    # -----------------------------------------------------

    featured_image = db.Column(
        db.String(500),
        nullable=True
    )

    # -----------------------------------------------------
    # PAGE STATUS
    #
    # draft
    # published
    # private
    # -----------------------------------------------------

    status = db.Column(
        db.String(20),
        default="draft",
        nullable=False,
        index=True
    )

    # -----------------------------------------------------
    # PAGE TEMPLATE
    #
    # default
    # full-width
    # landing
    # etc.
    # -----------------------------------------------------

    template = db.Column(
        db.String(100),
        default="default",
        nullable=False
    )

    # -----------------------------------------------------
    # SEO / INDEXING CONTROL
    # -----------------------------------------------------

    seo_title = db.Column(
        db.String(255),
        nullable=True
    )

    seo_description = db.Column(
        db.Text,
        nullable=True
    )

    seo_keywords = db.Column(
        db.String(500),
        nullable=True
    )

    canonical_url = db.Column(
        db.String(500),
        nullable=True
    )

    robots = db.Column(
        db.String(100),
        default="index, follow",
        nullable=False
    )

    # -----------------------------------------------------
    # SOCIAL / OPEN GRAPH
    # -----------------------------------------------------

    og_title = db.Column(
        db.String(255),
        nullable=True
    )

    og_description = db.Column(
        db.Text,
        nullable=True
    )

    og_image = db.Column(
        db.String(500),
        nullable=True
    )

    # -----------------------------------------------------
    # PUBLISH DATE
    # -----------------------------------------------------

    publish_date = db.Column(
        db.DateTime,
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
    # STATUS HELPERS
    # =====================================================

    def is_published(self):
        return self.status == "published"

    # -----------------------------------------------------

    def is_draft(self):
        return self.status == "draft"

    # -----------------------------------------------------

    def is_private(self):
        return self.status == "private"

    # =====================================================
    # CONTENT HELPERS
    # =====================================================

    def has_content(self):
        return bool(
            self.content
            and self.content.strip()
        )

    # -----------------------------------------------------

    def has_featured_image(self):
        return bool(
            self.featured_image
            and self.featured_image.strip()
        )

    # =====================================================
    # SEO HELPERS
    # =====================================================

    def get_seo_title(self):
        if self.seo_title:
            return self.seo_title.strip()

        return self.title

    # -----------------------------------------------------

    def get_seo_description(self):
        if self.seo_description:
            return self.seo_description.strip()

        if self.content:
            text = self.content.strip()

            if len(text) > 160:
                return text[:157] + "..."

            return text

        return ""

    # -----------------------------------------------------

    def get_robots(self):
        if self.robots:
            return self.robots.strip()

        return "index, follow"

    # -----------------------------------------------------

    def get_canonical_url(self):
        if self.canonical_url:
            return self.canonical_url.strip()

        return None

    # =====================================================
    # URL / SLUG HELPERS
    # =====================================================

    def get_url_slug(self):
        return self.slug.strip() if self.slug else ""

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return f"<Page {self.title!r}>"
