# ============================================================
# RASBHAV BOOKS
# ADMIN MENU CMS ROUTES / API
# ============================================================
#
# ADMIN PANEL
#      ↓
# MENU CMS API
#      ↓
# DATABASE
#      ↓
# PUBLIC WEBSITE
#
# Features:
# - Menu CRUD
# - Search
# - Location filter
# - Active / inactive filter
# - Menu items listing
# - Activate menu
# - Deactivate menu
# - Safe validation
# - Central admin authentication
# ============================================================


from flask import Blueprint, request, jsonify

from app import db

from app.models.menu import Menu
from app.models.menu_item import MenuItem

from app.routes.admin import admin_required


# ============================================================
# BLUEPRINT
# ============================================================

admin_menu_bp = Blueprint(
    "admin_menu",
    __name__,
    url_prefix="/api/admin/menus"
)


# ============================================================
# ALLOWED LOCATIONS
# ============================================================

ALLOWED_LOCATIONS = {
    "header",
    "footer",
    "mobile",
    "sidebar",
    "custom"
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
        "enabled"
    }:
        return True

    if value in {
        "0",
        "false",
        "no",
        "off",
        "inactive",
        "disabled"
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
# MENU ITEM SERIALIZER
# ============================================================

def menu_item_to_dict(item):

    return {

        "id":
            item.id,

        "menu_id":
            item.menu_id,

        "name":
            item.name,

        "item_type":
            item.item_type,

        "url":
            item.url,

        "page_id":
            item.page_id,

        "book_id":
            item.book_id,

        "category_id":
            item.category_id,

        "open_new_tab":
            bool(item.open_new_tab),

        "position":
            item.position,

        "is_active":
            bool(item.is_active),

        "page": (
            {
                "id": item.page.id,
                "title": item.page.title,
                "slug": item.page.slug
            }
            if item.page
            else None
        ),

        "book": (
            {
                "id": item.book.id,
                "title": item.book.title,
                "slug": item.book.slug
            }
            if item.book
            else None
        ),

        "category": (
            {
                "id": item.category.id,
                "name": item.category.name,
                "slug": item.category.slug
            }
            if item.category
            else None
        ),

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
# MENU SERIALIZER
# ============================================================

def menu_to_dict(
    menu,
    include_items=True
):

    data = {

        "id":
            menu.id,

        "name":
            menu.get_name(),

        "location":
            menu.get_location(),

        "is_active":
            bool(menu.is_active),

        "description":
            menu.description,

        "has_description":
            menu.has_description(),

        "created_at": (
            menu.created_at.isoformat()
            if menu.created_at
            else None
        ),

        "updated_at": (
            menu.updated_at.isoformat()
            if menu.updated_at
            else None
        )
    }

    # --------------------------------------------------------
    # ITEMS
    # --------------------------------------------------------

    if include_items:

        try:

            items = (
                MenuItem.query
                .filter_by(
                    menu_id=menu.id
                )
                .order_by(
                    MenuItem.position.asc(),
                    MenuItem.id.asc()
                )
                .all()
            )

            data["items"] = [
                menu_item_to_dict(item)
                for item in items
            ]

            data["item_count"] = len(items)

            data["active_item_count"] = sum(
                1
                for item in items
                if item.is_active
            )

        except Exception:

            data["items"] = []

            data["item_count"] = 0

            data["active_item_count"] = 0

    return data


# ============================================================
# GET ALL MENUS
# ============================================================

@admin_menu_bp.route(
    "",
    methods=["GET"]
)
@admin_menu_bp.route(
    "/",
    methods=["GET"]
)
def get_menus():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        query = Menu.query

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
                    Menu.name.ilike(pattern),
                    Menu.location.ilike(pattern),
                    Menu.description.ilike(pattern)
                )
            )

        # ----------------------------------------------------
        # LOCATION
        # ----------------------------------------------------

        location = clean_string(
            request.args.get("location")
        )

        if location:

            location = location.lower()

            query = query.filter(
                Menu.location == location
            )

        # ----------------------------------------------------
        # ACTIVE FILTER
        # ----------------------------------------------------

        is_active = parse_bool(
            request.args.get("is_active")
        )

        if is_active is not None:

            query = query.filter(
                Menu.is_active == is_active
            )

        # ----------------------------------------------------
        # ORDER
        # ----------------------------------------------------

        menus = (
            query
            .order_by(
                Menu.name.asc(),
                Menu.id.asc()
            )
            .all()
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

        menus = menus[:limit]

        return jsonify({

            "success":
                True,

            "count":
                len(menus),

            "menus":
                [
                    menu_to_dict(menu)
                    for menu in menus
                ]

        }), 200

    except Exception as error:

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load menus.",

            "error":
                str(error)

        }), 500


# ============================================================
# GET SINGLE MENU
# ============================================================

@admin_menu_bp.route(
    "/<int:menu_id>",
    methods=["GET"]
)
def get_menu(menu_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    menu = Menu.query.get(menu_id)

    if not menu:

        return jsonify({

            "success":
                False,

            "message":
                "Menu not found."

        }), 404

    return jsonify({

        "success":
            True,

        "menu":
            menu_to_dict(menu)

    }), 200


# ============================================================
# GET MENU ITEMS
# ============================================================

@admin_menu_bp.route(
    "/<int:menu_id>/items",
    methods=["GET"]
)
def get_menu_items(menu_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    menu = Menu.query.get(menu_id)

    if not menu:

        return jsonify({

            "success":
                False,

            "message":
                "Menu not found."

        }), 404

    try:

        items = (
            MenuItem.query
            .filter_by(
                menu_id=menu.id
            )
            .order_by(
                MenuItem.position.asc(),
                MenuItem.id.asc()
            )
            .all()
        )

        return jsonify({

            "success":
                True,

            "menu":
                {
                    "id": menu.id,
                    "name": menu.name,
                    "location": menu.location
                },

            "count":
                len(items),

            "items":
                [
                    menu_item_to_dict(item)
                    for item in items
                ]

        }), 200

    except Exception as error:

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load menu items.",

            "error":
                str(error)

        }), 500


# ============================================================
# CREATE MENU
# ============================================================

@admin_menu_bp.route(
    "",
    methods=["POST"]
)
@admin_menu_bp.route(
    "/",
    methods=["POST"]
)
def create_menu():

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
    # NAME
    # --------------------------------------------------------

    name = clean_string(
        data.get("name")
    )

    if not name:

        return jsonify({

            "success":
                False,

            "message":
                "Menu name is required."

        }), 400

    # --------------------------------------------------------
    # LOCATION
    # --------------------------------------------------------

    location = clean_string(
        data.get("location"),
        "custom"
    ).lower()

    if location not in ALLOWED_LOCATIONS:

        return jsonify({

            "success":
                False,

            "message":
                (
                    "Invalid menu location. "
                    "Allowed values: "
                    "header, footer, mobile, sidebar, custom."
                )

        }), 400

    # --------------------------------------------------------
    # ACTIVE
    # --------------------------------------------------------

    is_active = parse_bool(
        data.get("is_active"),
        True
    )

    # --------------------------------------------------------
    # CREATE
    # --------------------------------------------------------

    menu = Menu(

        name=name,

        location=location,

        is_active=is_active,

        description=clean_string(
            data.get("description")
        )
    )

    try:

        db.session.add(menu)

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Menu created successfully.",

            "menu":
                menu_to_dict(menu)

        }), 201

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to create menu.",

            "error":
                str(error)

        }), 500


# ============================================================
# UPDATE MENU
# ============================================================

@admin_menu_bp.route(
    "/<int:menu_id>",
    methods=["PUT", "PATCH"]
)
def update_menu(menu_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    menu = Menu.query.get(menu_id)

    if not menu:

        return jsonify({

            "success":
                False,

            "message":
                "Menu not found."

        }), 404

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    # --------------------------------------------------------
    # NAME
    # --------------------------------------------------------

    if "name" in data:

        name = clean_string(
            data.get("name")
        )

        if not name:

            return jsonify({

                "success":
                    False,

                "message":
                    "Menu name cannot be empty."

            }), 400

        menu.name = name

    # --------------------------------------------------------
    # LOCATION
    # --------------------------------------------------------

    if "location" in data:

        location = clean_string(
            data.get("location")
        )

        if not location:

            return jsonify({

                "success":
                    False,

                "message":
                    "Menu location cannot be empty."

            }), 400

        location = location.lower()

        if location not in ALLOWED_LOCATIONS:

            return jsonify({

                "success":
                    False,

                "message":
                    (
                        "Invalid menu location. "
                        "Allowed values: "
                        "header, footer, mobile, "
                        "sidebar, custom."
                    )

            }), 400

        menu.location = location

    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    if "description" in data:

        menu.description = clean_string(
            data.get("description")
        )

    # --------------------------------------------------------
    # ACTIVE
    # --------------------------------------------------------

    if "is_active" in data:

        is_active = parse_bool(
            data.get("is_active")
        )

        if is_active is None:

            return jsonify({

                "success":
                    False,

                "message":
                    "Invalid is_active value."

            }), 400

        menu.is_active = is_active

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    try:

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Menu updated successfully.",

            "menu":
                menu_to_dict(menu)

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to update menu.",

            "error":
                str(error)

        }), 500


# ============================================================
# DELETE MENU
# ============================================================

@admin_menu_bp.route(
    "/<int:menu_id>",
    methods=["DELETE"]
)
def delete_menu(menu_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    menu = Menu.query.get(menu_id)

    if not menu:

        return jsonify({

            "success":
                False,

            "message":
                "Menu not found."

        }), 404

    try:

        # ----------------------------------------------------
        # DELETE MENU ITEMS FIRST
        # ----------------------------------------------------

        MenuItem.query.filter_by(
            menu_id=menu.id
        ).delete(
            synchronize_session=False
        )

        # ----------------------------------------------------
        # DELETE MENU
        # ----------------------------------------------------

        db.session.delete(menu)

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Menu and its items deleted successfully."

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to delete menu.",

            "error":
                str(error)

        }), 500


# ============================================================
# ACTIVATE MENU
# ============================================================

@admin_menu_bp.route(
    "/<int:menu_id>/activate",
    methods=["POST"]
)
def activate_menu(menu_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    menu = Menu.query.get(menu_id)

    if not menu:

        return jsonify({

            "success":
                False,

            "message":
                "Menu not found."

        }), 404

    try:

        menu.activate()

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Menu activated successfully.",

            "menu":
                menu_to_dict(menu)

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to activate menu.",

            "error":
                str(error)

        }), 500


# ============================================================
# DEACTIVATE MENU
# ============================================================

@admin_menu_bp.route(
    "/<int:menu_id>/deactivate",
    methods=["POST"]
)
def deactivate_menu(menu_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    menu = Menu.query.get(menu_id)

    if not menu:

        return jsonify({

            "success":
                False,

            "message":
                "Menu not found."

        }), 404

    try:

        menu.deactivate()

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Menu deactivated successfully.",

            "menu":
                menu_to_dict(menu)

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to deactivate menu.",

            "error":
                str(error)

        }), 500


# ============================================================
# MENU SUMMARY
# ============================================================

@admin_menu_bp.route(
    "/summary",
    methods=["GET"]
)
def menu_summary():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        total = Menu.query.count()

        active = (
            Menu.query
            .filter(
                Menu.is_active.is_(True)
            )
            .count()
        )

        inactive = (
            Menu.query
            .filter(
                Menu.is_active.is_(False)
            )
            .count()
        )

        return jsonify({

            "success":
                True,

            "summary":
                {

                    "total":
                        total,

                    "active":
                        active,

                    "inactive":
                        inactive
                }

        }), 200

    except Exception as error:

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load menu summary.",

            "error":
                str(error)

        }), 500
