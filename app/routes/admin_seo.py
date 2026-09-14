# ============================================================
# RASBHAV BOOKS
# ADMIN SEO ROUTES / API
# ============================================================
#
# ADMIN PANEL
#      ↓
# SEO MANAGEMENT API
#      ↓
# SEO DATABASE
#      ↓
# PUBLIC WEBSITE
#
# Supports:
# - Book SEO
# - Chapter SEO
# - Category SEO
# - Author SEO
# - Page SEO
# - Home SEO
# - Site SEO
# - Meta title
# - Meta description
# - Focus keyword
# - Canonical URL
# - Robots
# - Open Graph
# - OG Image
# - JSON-LD Schema
# - Search / filtering
# - Duplicate protection
# - Entity validation
# - Safe rollback
# ============================================================


from flask import Blueprint, request, jsonify

from app import db

from app.models.seo import SEO
from app.models.book import Book
from app.models.chapter import Chapter
from app.models.category import Category
from app.models.author import Author
from app.models.page import Page

from app.routes.admin import admin_required


# ============================================================
# BLUEPRINT
# ============================================================

admin_seo_bp = Blueprint(
    "admin_seo",
    __name__,
    url_prefix="/api/admin/seo"
)


# ============================================================
# CONSTANTS
# ============================================================

ENTITY_TYPES = {
    "book",
    "chapter",
    "category",
    "author",
    "page",
    "home",
    "site"
}


# ============================================================
# HELPERS
# ============================================================

def clean_string(value, default=None):

    if value is None:
        return default

    value = str(value).strip()

    if not value:
        return default

    return value


def parse_int(value, default=None):

    if value is None:
        return default

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# ============================================================
# SEO SERIALIZER
# ============================================================

def seo_to_dict(item):

    return {

        "id":
            item.id,

        "entity_type":
            item.entity_type,

        "entity_id":
            item.entity_id,

        "meta_title":
            item.meta_title,

        "meta_description":
            item.meta_description,

        "focus_keyword":
            item.focus_keyword,

        "canonical_url":
            item.canonical_url,

        "robots":
            item.get_robots(),

        "og_title":
            item.og_title,

        "og_description":
            item.og_description,

        "og_image":
            item.og_image,

        "schema_data":
            item.schema_data,

        "schema":
            item.get_schema(),

        "has_open_graph":
            item.has_open_graph(),

        "has_schema":
            item.has_schema(),

        "created_at": (
            item.created_at.isoformat()
            if item.created_at
            else None
        ),

        "updated_at": (
            item.updated_at.isoformat()
            if item.updated_at
            else None
        )
    }


# ============================================================
# ENTITY LOOKUP
# ============================================================

def get_entity(
    entity_type,
    entity_id
):

    if entity_type == "home":
        return True

    if entity_type == "site":
        return True

    if entity_id is None:
        return None

    models = {

        "book":
            Book,

        "chapter":
            Chapter,

        "category":
            Category,

        "author":
            Author,

        "page":
            Page
    }

    model = models.get(
        entity_type
    )

    if not model:
        return None

    return model.query.get(
        entity_id
    )


# ============================================================
# VALIDATE ENTITY
# ============================================================

def validate_entity(
    entity_type,
    entity_id
):

    if entity_type not in ENTITY_TYPES:

        raise ValueError(
            "Invalid entity_type. "
            "Allowed: "
            + ", ".join(
                sorted(
                    ENTITY_TYPES
                )
            )
        )

    # Home/site do not require an ID.
    if entity_type in {
        "home",
        "site"
    }:

        return

    if entity_id is None:

        raise ValueError(
            "entity_id is required for "
            + entity_type
            + " SEO."
        )

    entity_id = parse_int(
        entity_id
    )

    if entity_id is None:

        raise ValueError(
            "entity_id must be an integer."
        )

    entity = get_entity(
        entity_type,
        entity_id
    )

    if not entity:

        raise LookupError(
            f"{entity_type.capitalize()} "
            f"with ID {entity_id} not found."
        )


# ============================================================
# NORMALIZE SEO DATA
# ============================================================

def normalize_seo_data(data):

    result = {}

    result["meta_title"] = clean_string(
        data.get(
            "meta_title"
        )
    )

    result["meta_description"] = clean_string(
        data.get(
            "meta_description"
        )
    )

    result["focus_keyword"] = clean_string(
        data.get(
            "focus_keyword"
        )
    )

    result["canonical_url"] = clean_string(
        data.get(
            "canonical_url"
        )
    )

    result["robots"] = clean_string(
        data.get(
            "robots"
        ),
        "index, follow"
    )

    result["og_title"] = clean_string(
        data.get(
            "og_title"
        )
    )

    result["og_description"] = clean_string(
        data.get(
            "og_description"
        )
    )

    result["og_image"] = clean_string(
        data.get(
            "og_image"
        )
    )

    return result


# ============================================================
# SET SCHEMA
# ============================================================

def apply_schema(
    item,
    schema_value
):

    if schema_value is None:

        item.set_schema(
            None
        )

        return

    item.set_schema(
        schema_value
    )


# ============================================================
# GET ALL SEO
# ============================================================

@admin_seo_bp.route(
    "",
    methods=["GET"]
)
@admin_seo_bp.route(
    "/",
    methods=["GET"]
)
def get_seo_settings():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        query = SEO.query

        # ----------------------------------------------------
        # ENTITY TYPE FILTER
        # ----------------------------------------------------

        entity_type = clean_string(
            request.args.get(
                "entity_type"
            )
        )

        if entity_type:

            entity_type = (
                entity_type.lower()
            )

            if entity_type not in ENTITY_TYPES:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Invalid entity_type."

                }), 400

            query = query.filter(
                SEO.entity_type
                == entity_type
            )

        # ----------------------------------------------------
        # ENTITY ID FILTER
        # ----------------------------------------------------

        if "entity_id" in request.args:

            entity_id = parse_int(
                request.args.get(
                    "entity_id"
                )
            )

            if entity_id is None:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Invalid entity_id."

                }), 400

            query = query.filter(
                SEO.entity_id
                == entity_id
            )

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        search = clean_string(
            request.args.get(
                "search"
            )
        )

        if search:

            pattern = f"%{search}%"

            query = query.filter(
                db.or_(
                    SEO.meta_title.ilike(
                        pattern
                    ),

                    SEO.meta_description.ilike(
                        pattern
                    ),

                    SEO.focus_keyword.ilike(
                        pattern
                    ),

                    SEO.entity_type.ilike(
                        pattern
                    )
                )
            )

        # ----------------------------------------------------
        # FETCH
        # ----------------------------------------------------

        seo_settings = (
            query
            .order_by(
                SEO.id.desc()
            )
            .all()
        )

        return jsonify({

            "success":
                True,

            "count":
                len(seo_settings),

            "seo_settings": [

                seo_to_dict(
                    item
                )

                for item in seo_settings
            ]

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load SEO settings.",

            "error":
                str(error)

        }), 500


# ============================================================
# GET SINGLE SEO
# ============================================================

@admin_seo_bp.route(
    "/<int:seo_id>",
    methods=["GET"]
)
def get_seo(seo_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        item = SEO.query.get(
            seo_id
        )

        if not item:

            return jsonify({

                "success":
                    False,

                "message":
                    "SEO settings not found."

            }), 404

        return jsonify({

            "success":
                True,

            "seo":
                seo_to_dict(
                    item
                )

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load SEO settings.",

            "error":
                str(error)

        }), 500


# ============================================================
# GET SEO BY ENTITY
# ============================================================

@admin_seo_bp.route(
    "/entity/<string:entity_type>/<int:entity_id>",
    methods=["GET"]
)
def get_seo_by_entity(
    entity_type,
    entity_id
):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        entity_type = (
            entity_type.strip().lower()
        )

        if entity_type not in ENTITY_TYPES:

            return jsonify({

                "success":
                    False,

                "message":
                    "Invalid entity_type."

            }), 400

        if entity_type in {
            "home",
            "site"
        }:

            return jsonify({

                "success":
                    False,

                "message":
                    "Home and site SEO do not use entity IDs."

            }), 400

        item = (
            SEO.query
            .filter_by(
                entity_type=entity_type,
                entity_id=entity_id
            )
            .first()
        )

        if not item:

            return jsonify({

                "success":
                    True,

                "exists":
                    False,

                "seo":
                    None

            }), 200

        return jsonify({

            "success":
                True,

            "exists":
                True,

            "seo":
                seo_to_dict(
                    item
                )

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load entity SEO.",

            "error":
                str(error)

        }), 500


# ============================================================
# GET HOME SEO
# ============================================================

@admin_seo_bp.route(
    "/home",
    methods=["GET"]
)
def get_home_seo():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        item = (
            SEO.query
            .filter_by(
                entity_type="home",
                entity_id=None
            )
            .first()
        )

        return jsonify({

            "success":
                True,

            "exists":
                item is not None,

            "seo":
                (
                    seo_to_dict(item)
                    if item
                    else None
                )

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load home SEO.",

            "error":
                str(error)

        }), 500


# ============================================================
# GET SITE SEO
# ============================================================

@admin_seo_bp.route(
    "/site",
    methods=["GET"]
)
def get_site_seo():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        item = (
            SEO.query
            .filter_by(
                entity_type="site",
                entity_id=None
            )
            .first()
        )

        return jsonify({

            "success":
                True,

            "exists":
                item is not None,

            "seo":
                (
                    seo_to_dict(item)
                    if item
                    else None
                )

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load site SEO.",

            "error":
                str(error)

        }), 500


# ============================================================
# CREATE SEO
# ============================================================

@admin_seo_bp.route(
    "",
    methods=["POST"]
)
@admin_seo_bp.route(
    "/",
    methods=["POST"]
)
def create_seo():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(
        silent=True
    ) or {}

    try:

        # ----------------------------------------------------
        # ENTITY
        # ----------------------------------------------------

        entity_type = clean_string(
            data.get(
                "entity_type"
            )
        )

        if not entity_type:

            return jsonify({

                "success":
                    False,

                "message":
                    "entity_type is required."

            }), 400

        entity_type = (
            entity_type.lower()
        )

        entity_id = data.get(
            "entity_id"
        )

        entity_id = (
            parse_int(
                entity_id
            )
            if entity_id is not None
            else None
        )

        # ----------------------------------------------------
        # VALIDATE ENTITY
        # ----------------------------------------------------

        validate_entity(
            entity_type,
            entity_id
        )

        # ----------------------------------------------------
        # DUPLICATE CHECK
        # ----------------------------------------------------

        existing = (
            SEO.query
            .filter_by(
                entity_type=entity_type,
                entity_id=entity_id
            )
            .first()
        )

        if existing:

            return jsonify({

                "success":
                    False,

                "message":
                    "SEO settings already exist for this entity.",

                "seo_id":
                    existing.id

            }), 409

        # ----------------------------------------------------
        # SEO DATA
        # ----------------------------------------------------

        seo_data = normalize_seo_data(
            data
        )

        item = SEO(

            entity_type=entity_type,

            entity_id=entity_id,

            meta_title=seo_data[
                "meta_title"
            ],

            meta_description=seo_data[
                "meta_description"
            ],

            focus_keyword=seo_data[
                "focus_keyword"
            ],

            canonical_url=seo_data[
                "canonical_url"
            ],

            robots=seo_data[
                "robots"
            ],

            og_title=seo_data[
                "og_title"
            ],

            og_description=seo_data[
                "og_description"
            ],

            og_image=seo_data[
                "og_image"
            ]
        )

        # ----------------------------------------------------
        # SCHEMA
        # ----------------------------------------------------

        if "schema" in data:

            apply_schema(
                item,
                data.get(
                    "schema"
                )
            )

        elif "schema_data" in data:

            apply_schema(
                item,
                data.get(
                    "schema_data"
                )
            )

        db.session.add(
            item
        )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "SEO settings created successfully.",

            "seo":
                seo_to_dict(
                    item
                )

        }), 201

    except ValueError as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                str(error)

        }), 400

    except LookupError as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                str(error)

        }), 404

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to create SEO settings.",

            "error":
                str(error)

        }), 500


# ============================================================
# UPDATE SEO
# ============================================================

@admin_seo_bp.route(
    "/<int:seo_id>",
    methods=["PUT", "PATCH"]
)
def update_seo(seo_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(
        silent=True
    ) or {}

    try:

        item = SEO.query.get(
            seo_id
        )

        if not item:

            return jsonify({

                "success":
                    False,

                "message":
                    "SEO settings not found."

            }), 404

        # ----------------------------------------------------
        # ENTITY TYPE
        # ----------------------------------------------------

        new_entity_type = data.get(
            "entity_type",
            item.entity_type
        )

        new_entity_type = clean_string(
            new_entity_type
        )

        if not new_entity_type:

            return jsonify({

                "success":
                    False,

                "message":
                    "entity_type cannot be empty."

            }), 400

        new_entity_type = (
            new_entity_type.lower()
        )

        # ----------------------------------------------------
        # ENTITY ID
        # ----------------------------------------------------

        if "entity_id" in data:

            new_entity_id = data.get(
                "entity_id"
            )

            new_entity_id = (
                parse_int(
                    new_entity_id
                )
                if new_entity_id is not None
                else None
            )

        else:

            new_entity_id = item.entity_id

        # ----------------------------------------------------
        # VALIDATE ENTITY
        # ----------------------------------------------------

        validate_entity(
            new_entity_type,
            new_entity_id
        )

        # ----------------------------------------------------
        # DUPLICATE CHECK
        # ----------------------------------------------------

        duplicate = (
            SEO.query
            .filter(
                SEO.entity_type
                == new_entity_type,

                SEO.entity_id
                == new_entity_id,

                SEO.id
                != item.id
            )
            .first()
        )

        if duplicate:

            return jsonify({

                "success":
                    False,

                "message":
                    "SEO settings already exist for this entity.",

                "seo_id":
                    duplicate.id

            }), 409

        item.entity_type = (
            new_entity_type
        )

        item.entity_id = (
            new_entity_id
        )

        # ----------------------------------------------------
        # SEO FIELDS
        # ----------------------------------------------------

        if any(
            key in data
            for key in (
                "meta_title",
                "meta_description",
                "focus_keyword",
                "canonical_url",
                "robots",
                "og_title",
                "og_description",
                "og_image"
            )
        ):

            seo_data = normalize_seo_data(
                {
                    **{
                        "meta_title":
                            item.meta_title,

                        "meta_description":
                            item.meta_description,

                        "focus_keyword":
                            item.focus_keyword,

                        "canonical_url":
                            item.canonical_url,

                        "robots":
                            item.robots,

                        "og_title":
                            item.og_title,

                        "og_description":
                            item.og_description,

                        "og_image":
                            item.og_image
                    },

                    **data
                }
            )

            item.meta_title = seo_data[
                "meta_title"
            ]

            item.meta_description = seo_data[
                "meta_description"
            ]

            item.focus_keyword = seo_data[
                "focus_keyword"
            ]

            item.canonical_url = seo_data[
                "canonical_url"
            ]

            item.robots = seo_data[
                "robots"
            ]

            item.og_title = seo_data[
                "og_title"
            ]

            item.og_description = seo_data[
                "og_description"
            ]

            item.og_image = seo_data[
                "og_image"
            ]

        # ----------------------------------------------------
        # SCHEMA
        # ----------------------------------------------------

        if "schema" in data:

            apply_schema(
                item,
                data.get(
                    "schema"
                )
            )

        elif "schema_data" in data:

            apply_schema(
                item,
                data.get(
                    "schema_data"
                )
            )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "SEO settings updated successfully.",

            "seo":
                seo_to_dict(
                    item
                )

        }), 200

    except ValueError as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                str(error)

        }), 400

    except LookupError as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                str(error)

        }), 404

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to update SEO settings.",

            "error":
                str(error)

        }), 500


# ============================================================
# DELETE SEO
# ============================================================

@admin_seo_bp.route(
    "/<int:seo_id>",
    methods=["DELETE"]
)
def delete_seo(seo_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        item = SEO.query.get(
            seo_id
        )

        if not item:

            return jsonify({

                "success":
                    False,

                "message":
                    "SEO settings not found."

            }), 404

        deleted_id = item.id

        db.session.delete(
            item
        )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "SEO settings deleted successfully.",

            "seo_id":
                deleted_id

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to delete SEO settings.",

            "error":
                str(error)

        }), 500


# ============================================================
# SEO PREVIEW
# ============================================================

@admin_seo_bp.route(
    "/<int:seo_id>/preview",
    methods=["GET"]
)
def preview_seo(seo_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        item = SEO.query.get(
            seo_id
        )

        if not item:

            return jsonify({

                "success":
                    False,

                "message":
                    "SEO settings not found."

            }), 404

        return jsonify({

            "success":
                True,

            "preview": {

                "title":
                    item.get_meta_title(),

                "description":
                    item.get_meta_description(),

                "robots":
                    item.get_robots(),

                "canonical":
                    item.canonical_url,

                "open_graph": {

                    "title":
                        item.og_title,

                    "description":
                        item.og_description,

                    "image":
                        item.og_image
                },

                "schema":
                    item.get_schema()
            }

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to generate SEO preview.",

            "error":
                str(error)

        }), 500
