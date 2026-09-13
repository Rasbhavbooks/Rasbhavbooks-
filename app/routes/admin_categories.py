from flask import Blueprint, request, jsonify, session

from app import db
from app.models.category import Category


admin_categories_bp = Blueprint(
    "admin_categories",
    __name__,
    url_prefix="/api/admin/categories"
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
# CATEGORY SERIALIZER
# =========================================================

def category_data(category):

    return {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "description": category.description,
        "image": category.image,
        "parent_id": category.parent_id,

        "created_at": (
            category.created_at.isoformat()
            if category.created_at else None
        ),

        "updated_at": (
            category.updated_at.isoformat()
            if category.updated_at else None
        )
    }


# =========================================================
# GET ALL CATEGORIES
# =========================================================

@admin_categories_bp.route("", methods=["GET"])
def get_categories():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    categories = Category.query.order_by(
        Category.name.asc()
    ).all()

    return jsonify({
        "success": True,
        "count": len(categories),
        "categories": [
            category_data(category)
            for category in categories
        ]
    })


# =========================================================
# GET SINGLE CATEGORY
# =========================================================

@admin_categories_bp.route(
    "/<int:category_id>",
    methods=["GET"]
)
def get_category(category_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    category = Category.query.get_or_404(
        category_id
    )

    return jsonify({
        "success": True,
        "category": category_data(category)
    })


# =========================================================
# CREATE CATEGORY
# =========================================================

@admin_categories_bp.route("", methods=["POST"])
def create_category():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(
        silent=True
    ) or {}

    name = str(
        data.get("name", "")
    ).strip()

    slug = str(
        data.get("slug", "")
    ).strip()

    if not name:

        return jsonify({
            "success": False,
            "message": "Category name is required."
        }), 400

    if not slug:

        return jsonify({
            "success": False,
            "message": "Category slug is required."
        }), 400


    # =====================================================
    # SLUG CHECK
    # =====================================================

    existing = Category.query.filter_by(
        slug=slug
    ).first()

    if existing:

        return jsonify({
            "success": False,
            "message": "Category slug already exists."
        }), 409


    # =====================================================
    # PARENT CATEGORY
    # =====================================================

    parent_id = data.get("parent_id")

    if parent_id is not None:

        try:
            parent_id = int(parent_id)

        except (TypeError, ValueError):

            return jsonify({
                "success": False,
                "message": "Invalid parent_id."
            }), 400

        parent = Category.query.get(
            parent_id
        )

        if not parent:

            return jsonify({
                "success": False,
                "message": "Parent category not found."
            }), 404


    # =====================================================
    # CREATE
    # =====================================================

    category = Category(

        name=name,

        slug=slug,

        description=data.get(
            "description"
        ),

        image=data.get(
            "image"
        ),

        parent_id=parent_id
    )


    db.session.add(category)

    db.session.commit()


    return jsonify({
        "success": True,
        "message": "Category created successfully.",
        "category": category_data(category)
    }), 201


# =========================================================
# UPDATE CATEGORY
# =========================================================

@admin_categories_bp.route(
    "/<int:category_id>",
    methods=["PUT"]
)
def update_category(category_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    category = Category.query.get_or_404(
        category_id
    )

    data = request.get_json(
        silent=True
    ) or {}


    # =====================================================
    # NAME
    # =====================================================

    if "name" in data:

        name = str(
            data["name"]
        ).strip()

        if not name:

            return jsonify({
                "success": False,
                "message": "Category name cannot be empty."
            }), 400

        category.name = name


    # =====================================================
    # SLUG
    # =====================================================

    if "slug" in data:

        slug = str(
            data["slug"]
        ).strip()

        if not slug:

            return jsonify({
                "success": False,
                "message": "Category slug cannot be empty."
            }), 400

        existing = Category.query.filter(
            Category.slug == slug,
            Category.id != category.id
        ).first()

        if existing:

            return jsonify({
                "success": False,
                "message": "Category slug already exists."
            }), 409

        category.slug = slug


    # =====================================================
    # DESCRIPTION
    # =====================================================

    if "description" in data:

        category.description = data[
            "description"
        ]


    # =====================================================
    # IMAGE
    # =====================================================

    if "image" in data:

        category.image = data[
            "image"
        ]


    # =====================================================
    # PARENT CATEGORY
    # =====================================================

    if "parent_id" in data:

        parent_id = data[
            "parent_id"
        ]

        if parent_id is not None:

            try:
                parent_id = int(parent_id)

            except (TypeError, ValueError):

                return jsonify({
                    "success": False,
                    "message": "Invalid parent_id."
                }), 400


            # Prevent self-parent
            if parent_id == category.id:

                return jsonify({
                    "success": False,
                    "message": "A category cannot be its own parent."
                }), 400


            parent = Category.query.get(
                parent_id
            )

            if not parent:

                return jsonify({
                    "success": False,
                    "message": "Parent category not found."
                }), 404


        category.parent_id = parent_id


    # =====================================================
    # SAVE
    # =====================================================

    db.session.commit()


    return jsonify({
        "success": True,
        "message": "Category updated successfully.",
        "category": category_data(category)
    })


# =========================================================
# DELETE CATEGORY
# =========================================================

@admin_categories_bp.route(
    "/<int:category_id>",
    methods=["DELETE"]
)
def delete_category(category_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    category = Category.query.get_or_404(
        category_id
    )


    # =====================================================
    # MOVE CHILD CATEGORIES TO ROOT
    # =====================================================

    children = Category.query.filter_by(
        parent_id=category.id
    ).all()

    for child in children:

        child.parent_id = None


    # =====================================================
    # DELETE
    # =====================================================

    db.session.delete(category)

    db.session.commit()


    return jsonify({
        "success": True,
        "message": "Category deleted successfully."
    })
