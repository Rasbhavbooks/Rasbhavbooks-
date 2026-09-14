# ============================================================
# RASBHAV BOOKS
# ADMIN PAGES CMS ROUTES / API
# ============================================================
#
# ADMIN PANEL
#      ↓
# PAGE CMS API
#      ↓
# DATABASE
#      ↓
# PUBLIC WEBSITE
#
# Features:
# - Page CRUD
# - Search
# - Status filtering
# - Publish / Unpublish
# - SEO fields
# - Featured image
# - Template
# - Canonical URL
# - Robots
# - Open Graph
# - Pagination limit
# - Safe validation
# - Central admin authentication
# ============================================================


from datetime import datetime

from flask import Blueprint, request, jsonify

from app import db

from app.models.page import Page

from app.routes.admin import admin_required


# ============================================================
# BLUEPRINT
# ============================================================

admin_pages_bp = Blueprint(
    "admin_pages",
    __name__,
    url_prefix="/api/admin/pages"
)


# ============================================================
# CONSTANTS
# ============================================================

ALLOWED_STATUS = {
    "draft",
    "published",
    "private"
}


ALLOWED_TEMPLATES = {
    "default",
    "full_width",
    "landing",
    "blank"
}


# ============================================================
# HELPER
# ============================================================

def clean_string(value, default=None):

    if value is None:
        return default

    value = str(value).strip()

    if not value:
        return default

    return value


# ============================================================
# BOOLEAN PARSER
# ============================================================

def parse_bool(value, default=None):

    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        return bool(value)

    value = str(value).strip().lower()

    if value in {
        "1",
        "true",
        "yes",
        "on",
        "active",
        "published"
    }:
        return True

    if value in {
        "0",
        "false",
        "no",
        "off",
        "inactive",
        "draft"
    }:
        return False

    return default


# ============================================================
# INTEGER PARSER
# ============================================================

def parse_int(value, default=None):

    if value is None:
        return default

    try:
        return int(value)

    except (
        TypeError,
        ValueError
    ):
        return default


# ============================================================
# DATETIME PARSER
# ============================================================

def parse_datetime(value):

    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    value = str(value).strip()

    if not value:
        return None

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

    except (
        TypeError,
        ValueError
    ):
        return None


# ============================================================
# PAGE SERIALIZER
# ============================================================

def page_to_dict(page):

    return {

        "id":
            page.id,

        "title":
            page.title,

        "slug":
            page.slug,

        "content":
            page.content,

        "featured_image":
            page.featured_image,

        "status":
            page.status,

        "template":
            page.template,

        "seo_title":
            page.seo_title,

        "seo_description":
            page.seo_description,

        "seo_keywords":
            page.seo_keywords,

        "canonical_url":
            page.canonical_url,

        "robots":
            page.robots,

        "og_title":
            page.og_title,

        "og_description":
            page.og_description,

        "og_image":
            page.og_image,

        "publish_date": (
            page.publish_date.isoformat()
            if page.publish_date
            else None
        ),

        "is_published":
            page.is_published(),

        "is_draft":
            page.is_draft(),

        "is_private":
            page.is_private(),

        "has_content":
            page.has_content(),

        "has_featured_image":
            page.has_featured_image(),

        "created_at": (
            page.created_at.isoformat()
            if page.created_at
            else None
        ),

        "updated_at": (
            page.updated_at.isoformat()
            if page.updated_at
            else None
        )
    }


# ============================================================
# GET ALL PAGES
# ============================================================

@admin_pages_bp.route(
    "",
    methods=["GET"]
)
@admin_pages_bp.route(
    "/",
    methods=["GET"]
)
def get_pages():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        query = Page.query

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        search = clean_string(
            request.args.get("search")
        )

        if search:

            pattern = f"%{search}%"

            query = query.filter(
                db.or_(
                    Page.title.ilike(pattern),
                    Page.slug.ilike(pattern),
                    Page.content.ilike(pattern)
                )
            )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        status = clean_string(
            request.args.get("status")
        )

        if status:

            status = status.lower()

            if status not in ALLOWED_STATUS:

                return jsonify({
                    "success": False,
                    "message": (
                        "Invalid status. "
                        "Allowed values: "
                        "draft, published, private."
                    )
                }), 400

            query = query.filter(
                Page.status == status
            )

        # ----------------------------------------------------
        # PUBLISHED FILTER
        # ----------------------------------------------------

        published = parse_bool(
            request.args.get("published")
        )

        if published is not None:

            if published:

                query = query.filter(
                    Page.status == "published"
                )

            else:

                query = query.filter(
                    Page.status != "published"
                )

        # ----------------------------------------------------
        # TEMPLATE FILTER
        # ----------------------------------------------------

        template = clean_string(
            request.args.get("template")
        )

        if template:

            query = query.filter(
                Page.template == template
            )

        # ----------------------------------------------------
        # ORDER
        # ----------------------------------------------------

        query = query.order_by(
            Page.created_at.desc(),
            Page.id.desc()
        )

        # ----------------------------------------------------
        # LIMIT
        # ----------------------------------------------------

        limit = parse_int(
            request.args.get("limit"),
            100
        )

        if limit is None or limit < 1:
            limit = 1

        if limit > 500:
            limit = 500

        pages = (
            query
            .limit(limit)
            .all()
        )

        return jsonify({

            "success":
                True,

            "count":
                len(pages),

            "pages":
                [
                    page_to_dict(page)
                    for page in pages
                ]

        }), 200

    except Exception as error:

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load pages.",

            "error":
                str(error)

        }), 500


# ============================================================
# GET SINGLE PAGE
# ============================================================

@admin_pages_bp.route(
    "/<int:page_id>",
    methods=["GET"]
)
def get_page(page_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    page = Page.query.get(page_id)

    if not page:

        return jsonify({

            "success":
                False,

            "message":
                "Page not found."

        }), 404

    return jsonify({

        "success":
            True,

        "page":
            page_to_dict(page)

    }), 200


# ============================================================
# CREATE PAGE
# ============================================================

@admin_pages_bp.route(
    "",
    methods=["POST"]
)
@admin_pages_bp.route(
    "/",
    methods=["POST"]
)
def create_page():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    # --------------------------------------------------------
    # REQUIRED
    # --------------------------------------------------------

    title = clean_string(
        data.get("title")
    )

    slug = clean_string(
        data.get("slug")
    )

    if not title:

        return jsonify({

            "success":
                False,

            "message":
                "Page title is required."

        }), 400

    if not slug:

        return jsonify({

            "success":
                False,

            "message":
                "Page slug is required."

        }), 400

    # --------------------------------------------------------
    # DUPLICATE SLUG
    # --------------------------------------------------------

    existing = Page.query.filter_by(
        slug=slug
    ).first()

    if existing:

        return jsonify({

            "success":
                False,

            "message":
                "A page with this slug already exists."

        }), 409

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    status = clean_string(
        data.get("status"),
        "draft"
    ).lower()

    if status not in ALLOWED_STATUS:

        return jsonify({

            "success":
                False,

            "message":
                (
                    "Invalid status. "
                    "Allowed values: "
                    "draft, published, private."
                )

        }), 400

    # --------------------------------------------------------
    # TEMPLATE
    # --------------------------------------------------------

    template = clean_string(
        data.get("template"),
        "default"
    )

    if template not in ALLOWED_TEMPLATES:

        # Custom template names are allowed.
        # Only empty template is rejected.

        if not template:

            template = "default"

    # --------------------------------------------------------
    # PUBLISH DATE
    # --------------------------------------------------------

    publish_date = parse_datetime(
        data.get("publish_date")
    )

    # --------------------------------------------------------
    # CREATE
    # --------------------------------------------------------

    page = Page(

        title=title,

        slug=slug,

        content=data.get(
            "content"
        ),

        featured_image=clean_string(
            data.get("featured_image")
        ),

        status=status,

        template=template,

        seo_title=clean_string(
            data.get("seo_title")
        ),

        seo_description=clean_string(
            data.get("seo_description")
        ),

        seo_keywords=clean_string(
            data.get("seo_keywords")
        ),

        canonical_url=clean_string(
            data.get("canonical_url")
        ),

        robots=clean_string(
            data.get("robots"),
            "index, follow"
        ),

        og_title=clean_string(
            data.get("og_title")
        ),

        og_description=clean_string(
            data.get("og_description")
        ),

        og_image=clean_string(
            data.get("og_image")
        ),

        publish_date=publish_date
    )

    try:

        db.session.add(page)

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Page created successfully.",

            "page":
                page_to_dict(page)

        }), 201

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to create page.",

            "error":
                str(error)

        }), 500


# ============================================================
# UPDATE PAGE
# ============================================================

@admin_pages_bp.route(
    "/<int:page_id>",
    methods=["PUT", "PATCH"]
)
def update_page(page_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    page = Page.query.get(page_id)

    if not page:

        return jsonify({

            "success":
                False,

            "message":
                "Page not found."

        }), 404

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    if "title" in data:

        title = clean_string(
            data.get("title")
        )

        if not title:

            return jsonify({

                "success":
                    False,

                "message":
                    "Page title cannot be empty."

            }), 400

        page.title = title

    # --------------------------------------------------------
    # SLUG
    # --------------------------------------------------------

    if "slug" in data:

        slug = clean_string(
            data.get("slug")
        )

        if not slug:

            return jsonify({

                "success":
                    False,

                "message":
                    "Page slug cannot be empty."

            }), 400

        existing = (
            Page.query
            .filter(
                Page.slug == slug,
                Page.id != page.id
            )
            .first()
        )

        if existing:

            return jsonify({

                "success":
                    False,

                "message":
                    "A page with this slug already exists."

            }), 409

        page.slug = slug

    # --------------------------------------------------------
    # CONTENT
    # --------------------------------------------------------

    if "content" in data:

        page.content = data.get(
            "content"
        )

    # --------------------------------------------------------
    # FEATURED IMAGE
    # --------------------------------------------------------

    if "featured_image" in data:

        page.featured_image = clean_string(
            data.get("featured_image")
        )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if "status" in data:

        status = clean_string(
            data.get("status")
        )

        if not status:

            status = "draft"

        status = status.lower()

        if status not in ALLOWED_STATUS:

            return jsonify({

                "success":
                    False,

                "message":
                    (
                        "Invalid status. "
                        "Allowed values: "
                        "draft, published, private."
                    )

            }), 400

        page.status = status

    # --------------------------------------------------------
    # TEMPLATE
    # --------------------------------------------------------

    if "template" in data:

        template = clean_string(
            data.get("template")
        )

        if not template:

            template = "default"

        page.template = template

    # --------------------------------------------------------
    # SEO TITLE
    # --------------------------------------------------------

    if "seo_title" in data:

        page.seo_title = clean_string(
            data.get("seo_title")
        )

    # --------------------------------------------------------
    # SEO DESCRIPTION
    # --------------------------------------------------------

    if "seo_description" in data:

        page.seo_description = clean_string(
            data.get("seo_description")
        )

    # --------------------------------------------------------
    # SEO KEYWORDS
    # --------------------------------------------------------

    if "seo_keywords" in data:

        page.seo_keywords = clean_string(
            data.get("seo_keywords")
        )

    # --------------------------------------------------------
    # CANONICAL
    # --------------------------------------------------------

    if "canonical_url" in data:

        page.canonical_url = clean_string(
            data.get("canonical_url")
        )

    # --------------------------------------------------------
    # ROBOTS
    # --------------------------------------------------------

    if "robots" in data:

        page.robots = clean_string(
            data.get("robots"),
            "index, follow"
        )

    # --------------------------------------------------------
    # OPEN GRAPH
    # --------------------------------------------------------

    if "og_title" in data:

        page.og_title = clean_string(
            data.get("og_title")
        )

    if "og_description" in data:

        page.og_description = clean_string(
            data.get("og_description")
        )

    if "og_image" in data:

        page.og_image = clean_string(
            data.get("og_image")
        )

    # --------------------------------------------------------
    # PUBLISH DATE
    # --------------------------------------------------------

    if "publish_date" in data:

        page.publish_date = parse_datetime(
            data.get("publish_date")
        )

    try:

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Page updated successfully.",

            "page":
                page_to_dict(page)

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to update page.",

            "error":
                str(error)

        }), 500


# ============================================================
# DELETE PAGE
# ============================================================

@admin_pages_bp.route(
    "/<int:page_id>",
    methods=["DELETE"]
)
def delete_page(page_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    page = Page.query.get(page_id)

    if not page:

        return jsonify({

            "success":
                False,

            "message":
                "Page not found."

        }), 404

    try:

        db.session.delete(page)

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Page deleted successfully."

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to delete page.",

            "error":
                str(error)

        }), 500


# ============================================================
# PUBLISH PAGE
# ============================================================

@admin_pages_bp.route(
    "/<int:page_id>/publish",
    methods=["POST"]
)
def publish_page(page_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    page = Page.query.get(page_id)

    if not page:

        return jsonify({

            "success":
                False,

            "message":
                "Page not found."

        }), 404

    try:

        page.status = "published"

        if not page.publish_date:

            page.publish_date = datetime.utcnow()

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Page published successfully.",

            "page":
                page_to_dict(page)

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to publish page.",

            "error":
                str(error)

        }), 500


# ============================================================
# UNPUBLISH PAGE
# ============================================================

@admin_pages_bp.route(
    "/<int:page_id>/unpublish",
    methods=["POST"]
)
def unpublish_page(page_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    page = Page.query.get(page_id)

    if not page:

        return jsonify({

            "success":
                False,

            "message":
                "Page not found."

        }), 404

    try:

        page.status = "draft"

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Page unpublished successfully.",

            "page":
                page_to_dict(page)

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to unpublish page.",

            "error":
                str(error)

        }), 500


# ============================================================
# PRIVATE PAGE
# ============================================================

@admin_pages_bp.route(
    "/<int:page_id>/private",
    methods=["POST"]
)
def make_page_private(page_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    page = Page.query.get(page_id)

    if not page:

        return jsonify({

            "success":
                False,

            "message":
                "Page not found."

        }), 404

    try:

        page.status = "private"

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Page marked as private.",

            "page":
                page_to_dict(page)

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to change page status.",

            "error":
                str(error)

        }), 500


# ============================================================
# PAGE PREVIEW DATA
# ============================================================

@admin_pages_bp.route(
    "/<int:page_id>/preview",
    methods=["GET"]
)
def preview_page(page_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    page = Page.query.get(page_id)

    if not page:

        return jsonify({

            "success":
                False,

            "message":
                "Page not found."

        }), 404

    return jsonify({

        "success":
            True,

        "preview":
            {

                "title":
                    page.get_seo_title(),

                "description":
                    page.get_seo_description(),

                "canonical_url":
                    page.get_canonical_url(),

                "robots":
                    page.get_robots(),

                "featured_image":
                    page.featured_image,

                "url_slug":
                    page.get_url_slug(),

                "status":
                    page.status,

                "template":
                    page.template
            },

        "page":
            page_to_dict(page)

    }), 200
