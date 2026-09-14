# ============================================================
# RASBHAV BOOKS
# ADMIN MENU ROUTES
# Flask + SQLAlchemy
# ============================================================

from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from app import db
from app.models.menu import Menu
from app.routes.admin import admin_required


admin_menu_bp = Blueprint(
    "admin_menu",
    __name__,
    url_prefix="/api/admin/menus"
)


# ============================================================
# HELPERS
# ============================================================

def serialize_menu(menu):
    return {
        "id": menu.id,
        "name": menu.name,
        "location": menu.location,
        "description": menu.description,
        "is_active": menu.is_active,
        "created_at": (
            menu.created_at.isoformat()
            if menu.created_at else None
        ),
        "updated_at": (
            menu.updated_at.isoformat()
            if menu.updated_at else None
        ),
    }


def get_json_data():
    return request.get_json(silent=True) or {}


# ============================================================
# GET ALL MENUS
# ============================================================

@admin_menu_bp.route("", methods=["GET"])
@admin_required
def get_menus():

    search = request.args.get("search", "").strip()
    location = request.args.get("location", "").strip()
    active = request.args.get("active", "").strip().lower()

    query = Menu.query

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    if search:
        search_pattern = f"%{search}%"

        query = query.filter(
            or_(
                Menu.name.ilike(search_pattern),
                Menu.location.ilike(search_pattern),
                Menu.description.ilike(search_pattern)
            )
        )

    # --------------------------------------------------------
    # LOCATION FILTER
    # --------------------------------------------------------

    if location:
        query = query.filter(
            Menu.location == location
        )

    # --------------------------------------------------------
    # ACTIVE FILTER
    # --------------------------------------------------------

    if active in ("1", "true", "yes"):
        query = query.filter(
            Menu.is_active.is_(True)
        )

    elif active in ("0", "false", "no"):
        query = query.filter(
            Menu.is_active.is_(False)
        )

    # --------------------------------------------------------
    # ORDER
    # --------------------------------------------------------

    menus = query.order_by(
        Menu.id.asc()
    ).all()

    return jsonify({
        "success": True,
        "count": len(menus),
        "menus": [
            serialize_menu(menu)
            for menu in menus
        ]
    }), 200


# ============================================================
# GET SINGLE MENU
# ============================================================

@admin_menu_bp.route("/<int:menu_id>", methods=["GET"])
@admin_required
def get_menu(menu_id):

    menu = Menu.query.get(menu_id)

    if not menu:
        return jsonify({
            "success": False,
            "message": "Menu not found"
        }), 404

    return jsonify({
        "success": True,
        "menu": serialize_menu(menu)
    }), 200


# ============================================================
# CREATE MENU
# ============================================================

@admin_menu_bp.route("", methods=["POST"])
@admin_required
def create_menu():

    data = get_json_data()

    name = str(
        data.get("name", "")
    ).strip()

    location = str(
        data.get("location", "")
    ).strip()

    description = str(
        data.get("description", "")
    ).strip()

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not name:
        return jsonify({
            "success": False,
            "message": "Menu name is required"
        }), 400

    if len(name) > 150:
        return jsonify({
            "success": False,
            "message": "Menu name is too long"
        }), 400

    if not location:
        return jsonify({
            "success": False,
            "message": "Menu location is required"
        }), 400

    if len(location) > 100:
        return jsonify({
            "success": False,
            "message": "Menu location is too long"
        }), 400

    # --------------------------------------------------------
    # DUPLICATE CHECK
    # --------------------------------------------------------

    existing = Menu.query.filter(
        or_(
            Menu.name == name,
            Menu.location == location
        )
    ).first()

    if existing:
        return jsonify({
            "success": False,
            "message": "A menu with the same name or location already exists"
        }), 409

    # --------------------------------------------------------
    # ACTIVE STATUS
    # --------------------------------------------------------

    is_active = data.get(
        "is_active",
        True
    )

    if not isinstance(is_active, bool):
        is_active = bool(is_active)

    # --------------------------------------------------------
    # CREATE
    # --------------------------------------------------------

    menu = Menu(
        name=name,
        location=location,
        description=description or None,
        is_active=is_active
    )

    try:
        db.session.add(menu)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Menu could not be created because of a database conflict"
        }), 409

    except Exception:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to create menu"
        }), 500

    return jsonify({
        "success": True,
        "message": "Menu created successfully",
        "menu": serialize_menu(menu)
    }), 201


# ============================================================
# UPDATE MENU
# ============================================================

@admin_menu_bp.route("/<int:menu_id>", methods=["PUT", "PATCH"])
@admin_required
def update_menu(menu_id):

    menu = Menu.query.get(menu_id)

    if not menu:
        return jsonify({
            "success": False,
            "message": "Menu not found"
        }), 404

    data = get_json_data()

    # --------------------------------------------------------
    # NAME
    # --------------------------------------------------------

    if "name" in data:

        name = str(
            data.get("name", "")
        ).strip()

        if not name:
            return jsonify({
                "success": False,
                "message": "Menu name cannot be empty"
            }), 400

        if len(name) > 150:
            return jsonify({
                "success": False,
                "message": "Menu name is too long"
            }), 400

        duplicate = Menu.query.filter(
            Menu.id != menu.id,
            Menu.name == name
        ).first()

        if duplicate:
            return jsonify({
                "success": False,
                "message": "Another menu already uses this name"
            }), 409

        menu.name = name

    # --------------------------------------------------------
    # LOCATION
    # --------------------------------------------------------

    if "location" in data:

        location = str(
            data.get("location", "")
        ).strip()

        if not location:
            return jsonify({
                "success": False,
                "message": "Menu location cannot be empty"
            }), 400

        if len(location) > 100:
            return jsonify({
                "success": False,
                "message": "Menu location is too long"
            }), 400

        duplicate = Menu.query.filter(
            Menu.id != menu.id,
            Menu.location == location
        ).first()

        if duplicate:
            return jsonify({
                "success": False,
                "message": "Another menu already uses this location"
            }), 409

        menu.location = location

    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    if "description" in data:

        description = str(
            data.get("description", "")
        ).strip()

        menu.description = (
            description
            if description
            else None
        )

    # --------------------------------------------------------
    # ACTIVE STATUS
    # --------------------------------------------------------

    if "is_active" in data:

        is_active = data.get(
            "is_active"
        )

        if not isinstance(is_active, bool):
            is_active = bool(is_active)

        menu.is_active = is_active

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    try:
        db.session.commit()

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Menu could not be updated because of a database conflict"
        }), 409

    except Exception:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to update menu"
        }), 500

    return jsonify({
        "success": True,
        "message": "Menu updated successfully",
        "menu": serialize_menu(menu)
    }), 200


# ============================================================
# ACTIVATE MENU
# ============================================================

@admin_menu_bp.route("/<int:menu_id>/activate", methods=["POST"])
@admin_required
def activate_menu(menu_id):

    menu = Menu.query.get(menu_id)

    if not menu:
        return jsonify({
            "success": False,
            "message": "Menu not found"
        }), 404

    menu.is_active = True

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to activate menu"
        }), 500

    return jsonify({
        "success": True,
        "message": "Menu activated successfully",
        "menu": serialize_menu(menu)
    }), 200


# ============================================================
# DEACTIVATE MENU
# ============================================================

@admin_menu_bp.route("/<int:menu_id>/deactivate", methods=["POST"])
@admin_required
def deactivate_menu(menu_id):

    menu = Menu.query.get(menu_id)

    if not menu:
        return jsonify({
            "success": False,
            "message": "Menu not found"
        }), 404

    menu.is_active = False

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to deactivate menu"
        }), 500

    return jsonify({
        "success": True,
        "message": "Menu deactivated successfully",
        "menu": serialize_menu(menu)
    }), 200


# ============================================================
# DELETE MENU
# ============================================================

@admin_menu_bp.route("/<int:menu_id>", methods=["DELETE"])
@admin_required
def delete_menu(menu_id):

    menu = Menu.query.get(menu_id)

    if not menu:
        return jsonify({
            "success": False,
            "message": "Menu not found"
        }), 404

    try:

        db.session.delete(menu)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Menu cannot be deleted because it is still being used"
        }), 409

    except Exception:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to delete menu"
        }), 500

    return jsonify({
        "success": True,
        "message": "Menu deleted successfully"
    }), 200
