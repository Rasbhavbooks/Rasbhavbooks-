from flask import Blueprint, request, jsonify, session

from app import db
from app.models.seo import SEO


admin_seo_bp = Blueprint(
    "admin_seo",
    __name__,
    url_prefix="/api/admin/seo"
)


# =========================================================
# ADMIN AUTH CHECK
# =========================================================

def admin_required():
    if not session.get("admin_id"):
        return jsonify({
            "success": False,
            "message": "Admin login required."
        }), 401

    return None


# =========================================================
# GET ALL SEO SETTINGS
# =========================================================

@admin_seo_bp.route("", methods=["GET"])
def get_seo_settings():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    entity_type = request.args.get(
        "entity_type",
        ""
    ).strip()

    entity_id = request.args.get(
        "entity_id",
        type=int
    )

    query = SEO.query

    if entity_type:
        query = query.filter_by(
            entity_type=entity_type
        )

    if entity_id is not None:
        query = query.filter_by(
            entity_id=entity_id
        )

    seo_settings = query.order_by(
        SEO.id.desc()
    ).all()

    return jsonify({
        "success": True,
        "count": len(seo_settings),
        "seo_settings": [
            {
                "id": item.id,
                "entity_type": item.entity_type,
                "entity_id": item.entity_id,
                "meta_title": item.meta_title,
                "meta_description": item.meta_description,
                "focus_keyword": item.focus_keyword,
                "canonical_url": item.canonical_url,
                "robots": item.robots,
                "og_title": item.og_title,
                "og_description": item.og_description,
                "og_image": item.og_image,
                "schema_data": item.schema_data,
                "created_at": (
                    item.created_at.isoformat()
                    if item.created_at else None
                ),
                "updated_at": (
                    item.updated_at.isoformat()
                    if item.updated_at else None
                )
            }
            for item in seo_settings
        ]
    })


# =========================================================
# GET SINGLE SEO
# =========================================================

@admin_seo_bp.route("/<int:seo_id>", methods=["GET"])
def get_seo(seo_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    item = SEO.query.get_or_404(seo_id)

    return jsonify({
        "success": True,
        "seo": {
            "id": item.id,
            "entity_type": item.entity_type,
            "entity_id": item.entity_id,
            "meta_title": item.meta_title,
            "meta_description": item.meta_description,
            "focus_keyword": item.focus_keyword,
            "canonical_url": item.canonical_url,
            "robots": item.robots,
            "og_title": item.og_title,
            "og_description": item.og_description,
            "og_image": item.og_image,
            "schema_data": item.schema_data
        }
    })


# =========================================================
# CREATE SEO
# =========================================================

@admin_seo_bp.route("", methods=["POST"])
def create_seo():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}

    entity_type = str(
        data.get("entity_type", "")
    ).strip()

    entity_id = data.get("entity_id")

    if not entity_type:
        return jsonify({
            "success": False,
            "message": "Entity type is required."
        }), 400

    if entity_type not in [
        "book",
        "chapter",
        "category",
        "author",
        "page",
        "home",
        "site"
    ]:
        return jsonify({
            "success": False,
            "message": "Invalid entity type."
        }), 400

    # Home and site SEO do not require entity_id.
    if entity_type in [
        "book",
        "chapter",
        "category",
        "author",
        "page"
    ] and entity_id is None:

        return jsonify({
            "success": False,
            "message": "Entity ID is required."
        }), 400

    existing_query = SEO.query.filter_by(
        entity_type=entity_type,
        entity_id=entity_id
    )

    if existing_query.first():

        return jsonify({
            "success": False,
            "message": "SEO settings already exist for this entity."
        }), 409

    item = SEO(
        entity_type=entity_type,
        entity_id=entity_id,
        meta_title=data.get("meta_title"),
        meta_description=data.get("meta_description"),
        focus_keyword=data.get("focus_keyword"),
        canonical_url=data.get("canonical_url"),
        robots=data.get(
            "robots",
            "index, follow"
        ),
        og_title=data.get("og_title"),
        og_description=data.get("og_description"),
        og_image=data.get("og_image"),
        schema_data=data.get("schema_data")
    )

    db.session.add(item)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "SEO settings created successfully.",
        "seo_id": item.id
    }), 201


# =========================================================
# UPDATE SEO
# =========================================================

@admin_seo_bp.route("/<int:seo_id>", methods=["PUT"])
def update_seo(seo_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    item = SEO.query.get_or_404(seo_id)

    data = request.get_json(silent=True) or {}

    if "entity_type" in data:

        entity_type = str(
            data["entity_type"]
        ).strip()

        if entity_type not in [
            "book",
            "chapter",
            "category",
            "author",
            "page",
            "home",
            "site"
        ]:
            return jsonify({
                "success": False,
                "message": "Invalid entity type."
            }), 400

        item.entity_type = entity_type

    if "entity_id" in data:
        item.entity_id = data["entity_id"]

    if "meta_title" in data:
        item.meta_title = data["meta_title"]

    if "meta_description" in data:
        item.meta_description = data["meta_description"]

    if "focus_keyword" in data:
        item.focus_keyword = data["focus_keyword"]

    if "canonical_url" in data:
        item.canonical_url = data["canonical_url"]

    if "robots" in data:
        item.robots = data["robots"]

    if "og_title" in data:
        item.og_title = data["og_title"]

    if "og_description" in data:
        item.og_description = data["og_description"]

    if "og_image" in data:
        item.og_image = data["og_image"]

    if "schema_data" in data:
        item.schema_data = data["schema_data"]

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "SEO settings updated successfully.",
        "seo_id": item.id
    })


# =========================================================
# DELETE SEO
# =========================================================

@admin_seo_bp.route("/<int:seo_id>", methods=["DELETE"])
def delete_seo(seo_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    item = SEO.query.get_or_404(seo_id)

    db.session.delete(item)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "SEO settings deleted successfully."
    })
