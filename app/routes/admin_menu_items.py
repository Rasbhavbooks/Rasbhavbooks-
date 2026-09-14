# =========================================================
# RASBHAV BOOKS
# ADMIN MENU ITEMS API
# app/routes/admin_menu_items.py
# =========================================================

from flask import Blueprint, request, jsonify

from sqlalchemy import or_

from app import db

from app.models.menu_item import MenuItem
from app.models.menu import Menu
from app.models.page import Page
from app.models.book import Book
from app.models.category import Category

from app.routes.admin import admin_required


# =========================================================
# BLUEPRINT
# =========================================================

admin_menu_items_bp = Blueprint(
    "admin_menu_items",
    __name__,
    url_prefix="/api/admin/menu-items"
)


# =========================================================
# CONSTANTS
# =========================================================

ALLOWED_ITEM_TYPES = {
    "custom_url",
    "page",
    "book",
    "category",
    "home",
    "books",
    "search",
}

MAX_LIMIT = 200


# =========================================================
# HELPERS
# =========================================================

def clean_string(value, default=None):
    if value is None:
        return default

    value = str(value).strip()

    return value if value else default


def parse_int(value, default=None, minimum=None):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default

    if minimum is not None and number < minimum:
        return default

    return number


def parse_bool(value, default=False):
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        return bool(value)

    value = str(value).strip().lower()

    if value in {
        "true",
        "1",
        "yes",
        "on",
        "active",
        "published",
    }:
        return True

    if value in {
        "false",
        "0",
        "no",
        "off",
        "inactive",
        "draft",
    }:
        return False

    return default


def serialize_datetime(value):
    if not value:
        return None

    return value.isoformat()


# =========================================================
# TARGET VALIDATION
# =========================================================

def validate_target(item_type, data):
    """
    Validate the target according to item_type.

    Returns:
        (success, error_message, target_data)
    """

    page_id = parse_int(data.get("page_id"), default=None, minimum=1)
    book_id = parse_int(data.get("book_id"), default=None, minimum=1)
    category_id = parse_int(
        data.get("category_id"),
        default=None,
        minimum=1
    )

    url = clean_string(data.get("url"))

    # -----------------------------------------------------
    # CUSTOM URL
    # -----------------------------------------------------

    if item_type == "custom_url":

        if not url:
            return (
                False,
                "URL is required for custom_url menu item.",
                None
            )

        return (
            True,
            None,
            {
                "url": url,
                "page_id": None,
                "book_id": None,
                "category_id": None,
            }
        )

    # -----------------------------------------------------
    # PAGE
    # -----------------------------------------------------

    if item_type == "page":

        if not page_id:
            return (
                False,
                "page_id is required for page menu item.",
                None
            )

        page = Page.query.get(page_id)

        if not page:
            return (
                False,
                "Selected page was not found.",
                None
            )

        return (
            True,
            None,
            {
                "url": None,
                "page_id": page.id,
                "book_id": None,
                "category_id": None,
            }
        )

    # -----------------------------------------------------
    # BOOK
    # -----------------------------------------------------

    if item_type == "book":

        if not book_id:
            return (
                False,
                "book_id is required for book menu item.",
                None
            )

        book = Book.query.get(book_id)

        if not book:
            return (
                False,
                "Selected book was not found.",
                None
            )

        return (
            True,
            None,
            {
                "url": None,
                "page_id": None,
                "book_id": book.id,
                "category_id": None,
            }
        )

    # -----------------------------------------------------
    # CATEGORY
    # -----------------------------------------------------

    if item_type == "category":

        if not category_id:
            return (
                False,
                "category_id is required for category menu item.",
                None
            )

        category = Category.query.get(category_id)

        if not category:
            return (
                False,
                "Selected category was not found.",
                None
            )

        return (
            True,
            None,
            {
                "url": None,
                "page_id": None,
                "book_id": None,
                "category_id": category.id,
            }
        )

    # -----------------------------------------------------
    # HOME / BOOKS / SEARCH
    # -----------------------------------------------------

    if item_type in {
        "home",
        "books",
        "search",
    }:

        return (
            True,
            None,
            {
                "url": None,
                "page_id": None,
                "book_id": None,
                "category_id": None,
            }
        )

    return (
        False,
        "Invalid menu item type.",
        None
    )


# =========================================================
# SERIALIZER
# =========================================================

def menu_item_to_dict(item, include_targets=True):

    data = {
        "id": item.id,

        "menu_id": item.menu_id,

        "name": item.name,

        "item_type": item.item_type,

        "url": item.url,

        "page_id": item.page_id,

        "book_id": item.book_id,

        "category_id": item.category_id,

        "open_new_tab": bool(item.open_new_tab),

        "position": item.position,

        "is_active": bool(item.is_active),

        "created_at": serialize_datetime(
            item.created_at
        ),

        "updated_at": serialize_datetime(
            item.updated_at
        ),
    }

    # -----------------------------------------------------
    # MENU
    # -----------------------------------------------------

    if item.menu:
        data["menu"] = {
            "id": item.menu.id,
            "name": item.menu.name,
            "location": item.menu.location,
            "is_active": bool(item.menu.is_active),
        }

    else:
        data["menu"] = None

    # -----------------------------------------------------
    # TARGET INFORMATION
    # -----------------------------------------------------

    if include_targets:

        data["target"] = None

        if item.item_type == "page" and item.page:
            data["target"] = {
                "type": "page",
                "id": item.page.id,
                "title": item.page.title,
                "slug": item.page.slug,
                "status": item.page.status,
            }

        elif item.item_type == "book" and item.book:
            data["target"] = {
                "type": "book",
                "id": item.book.id,
                "title": item.book.title,
                "slug": item.book.slug,
                "published": bool(item.book.published),
            }

        elif item.item_type == "category" and item.category:
            data["target"] = {
                "type": "category",
                "id": item.category.id,
                "name": item.category.name,
                "slug": item.category.slug,
            }

        elif item.item_type == "custom_url":
            data["target"] = {
                "type": "custom_url",
                "url": item.url,
            }

        elif item.item_type == "home":
            data["target"] = {
                "type": "home",
                "url": "/",
            }

        elif item.item_type == "books":
            data["target"] = {
                "type": "books",
                "url": "/books",
            }

        elif item.item_type == "search":
            data["target"] = {
                "type": "search",
                "url": "/search",
            }

    return data


# =========================================================
# GET ALL MENU ITEMS
# =========================================================

@admin_menu_items_bp.route("", methods=["GET"])
@admin_menu_items_bp.route("/", methods=["GET"])
def get_menu_items():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        query = MenuItem.query

        # -------------------------------------------------
        # MENU FILTER
        # -------------------------------------------------

        menu_id = request.args.get(
            "menu_id",
            type=int
        )

        if menu_id:
            query = query.filter(
                MenuItem.menu_id == menu_id
            )

        # -------------------------------------------------
        # ITEM TYPE FILTER
        # -------------------------------------------------

        item_type = clean_string(
            request.args.get("item_type")
        )

        if item_type:

            if item_type not in ALLOWED_ITEM_TYPES:
                return jsonify({
                    "success": False,
                    "message": "Invalid item_type."
                }), 400

            query = query.filter(
                MenuItem.item_type == item_type
            )

        # -------------------------------------------------
        # ACTIVE FILTER
        # -------------------------------------------------

        if "is_active" in request.args:

            is_active = parse_bool(
                request.args.get("is_active")
            )

            query = query.filter(
                MenuItem.is_active == is_active
            )

        # -------------------------------------------------
        # SEARCH
        # -------------------------------------------------

        search = clean_string(
            request.args.get("search")
        )

        if search:

            pattern = f"%{search}%"

            query = query.filter(
                or_(
                    MenuItem.name.ilike(pattern),
                    MenuItem.url.ilike(pattern),
                )
            )

        # -------------------------------------------------
        # ORDER
        # -------------------------------------------------

        query = query.order_by(
            MenuItem.menu_id.asc(),
            MenuItem.position.asc(),
            MenuItem.id.asc()
        )

        # -------------------------------------------------
        # LIMIT
        # -------------------------------------------------

        limit = parse_int(
            request.args.get("limit"),
            default=100,
            minimum=1
        )

        if limit > MAX_LIMIT:
            limit = MAX_LIMIT

        items = query.limit(limit).all()

        return jsonify({
            "success": True,
            "count": len(items),
            "items": [
                menu_item_to_dict(item)
                for item in items
            ]
        }), 200

    except Exception as exc:

        return jsonify({
            "success": False,
            "message": "Failed to load menu items.",
            "error": str(exc)
        }), 500


# =========================================================
# GET SINGLE MENU ITEM
# =========================================================

@admin_menu_items_bp.route(
    "/<int:item_id>",
    methods=["GET"]
)
def get_menu_item(item_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    item = MenuItem.query.get(item_id)

    if not item:
        return jsonify({
            "success": False,
            "message": "Menu item not found."
        }), 404

    return jsonify({
        "success": True,
        "item": menu_item_to_dict(item)
    }), 200


# =========================================================
# CREATE MENU ITEM
# =========================================================

@admin_menu_items_bp.route(
    "",
    methods=["POST"]
)
@admin_menu_items_bp.route(
    "/",
    methods=["POST"]
)
def create_menu_item():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}

    name = clean_string(
        data.get("name")
    )

    menu_id = parse_int(
        data.get("menu_id"),
        default=None,
        minimum=1
    )

    item_type = clean_string(
        data.get("item_type"),
        default="custom_url"
    ).lower()

    position = parse_int(
        data.get("position"),
        default=0,
        minimum=0
    )

    open_new_tab = parse_bool(
        data.get("open_new_tab"),
        default=False
    )

    is_active = parse_bool(
        data.get("is_active"),
        default=True
    )

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not name:
        return jsonify({
            "success": False,
            "message": "Menu item name is required."
        }), 400

    if not menu_id:
        return jsonify({
            "success": False,
            "message": "menu_id is required."
        }), 400

    if item_type not in ALLOWED_ITEM_TYPES:
        return jsonify({
            "success": False,
            "message": "Invalid menu item type."
        }), 400

    menu = Menu.query.get(menu_id)

    if not menu:
        return jsonify({
            "success": False,
            "message": "Menu not found."
        }), 404

    # -----------------------------------------------------
    # TARGET
    # -----------------------------------------------------

    valid, error, target = validate_target(
        item_type,
        data
    )

    if not valid:
        return jsonify({
            "success": False,
            "message": error
        }), 400

    # -----------------------------------------------------
    # AUTO POSITION
    # -----------------------------------------------------

    if "position" not in data:

        last_item = (
            MenuItem.query
            .filter_by(menu_id=menu.id)
            .order_by(MenuItem.position.desc())
            .first()
        )

        if last_item:
            position = last_item.position + 1

        else:
            position = 0

    # -----------------------------------------------------
    # CREATE
    # -----------------------------------------------------

    item = MenuItem(
        menu_id=menu.id,

        name=name,

        item_type=item_type,

        url=target["url"],

        page_id=target["page_id"],

        book_id=target["book_id"],

        category_id=target["category_id"],

        open_new_tab=open_new_tab,

        position=position,

        is_active=is_active,
    )

    try:

        db.session.add(item)

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Menu item created successfully.",
            "item": menu_item_to_dict(item)
        }), 201

    except Exception as exc:

        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to create menu item.",
            "error": str(exc)
        }), 500


# =========================================================
# UPDATE MENU ITEM
# =========================================================

@admin_menu_items_bp.route(
    "/<int:item_id>",
    methods=["PUT", "PATCH"]
)
def update_menu_item(item_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    item = MenuItem.query.get(item_id)

    if not item:
        return jsonify({
            "success": False,
            "message": "Menu item not found."
        }), 404

    data = request.get_json(silent=True) or {}

    # -----------------------------------------------------
    # NAME
    # -----------------------------------------------------

    if "name" in data:

        name = clean_string(
            data.get("name")
        )

        if not name:
            return jsonify({
                "success": False,
                "message": "Menu item name cannot be empty."
            }), 400

        item.name = name

    # -----------------------------------------------------
    # MENU
    # -----------------------------------------------------

    if "menu_id" in data:

        menu_id = parse_int(
            data.get("menu_id"),
            default=None,
            minimum=1
        )

        if not menu_id:
            return jsonify({
                "success": False,
                "message": "Invalid menu_id."
            }), 400

        menu = Menu.query.get(menu_id)

        if not menu:
            return jsonify({
                "success": False,
                "message": "Menu not found."
            }), 404

        item.menu_id = menu.id

    # -----------------------------------------------------
    # ITEM TYPE
    # -----------------------------------------------------

    item_type = item.item_type

    if "item_type" in data:

        item_type = clean_string(
            data.get("item_type")
        )

        if not item_type:
            return jsonify({
                "success": False,
                "message": "item_type cannot be empty."
            }), 400

        item_type = item_type.lower()

        if item_type not in ALLOWED_ITEM_TYPES:
            return jsonify({
                "success": False,
                "message": "Invalid item_type."
            }), 400

    # -----------------------------------------------------
    # TARGET
    # -----------------------------------------------------

    target_data = {
        "url": item.url,
        "page_id": item.page_id,
        "book_id": item.book_id,
        "category_id": item.category_id,
    }

    merged_data = dict(data)

    if "url" not in merged_data:
        merged_data["url"] = item.url

    if "page_id" not in merged_data:
        merged_data["page_id"] = item.page_id

    if "book_id" not in merged_data:
        merged_data["book_id"] = item.book_id

    if "category_id" not in merged_data:
        merged_data["category_id"] = item.category_id

    valid, error, target = validate_target(
        item_type,
        merged_data
    )

    if not valid:
        return jsonify({
            "success": False,
            "message": error
        }), 400

    item.item_type = item_type

    item.url = target["url"]

    item.page_id = target["page_id"]

    item.book_id = target["book_id"]

    item.category_id = target["category_id"]

    # -----------------------------------------------------
    # OPEN NEW TAB
    # -----------------------------------------------------

    if "open_new_tab" in data:

        item.open_new_tab = parse_bool(
            data.get("open_new_tab"),
            default=item.open_new_tab
        )

    # -----------------------------------------------------
    # POSITION
    # -----------------------------------------------------

    if "position" in data:

        position = parse_int(
            data.get("position"),
            default=None,
            minimum=0
        )

        if position is None:
            return jsonify({
                "success": False,
                "message": "Invalid position."
            }), 400

        item.position = position

    # -----------------------------------------------------
    # ACTIVE
    # -----------------------------------------------------

    if "is_active" in data:

        item.is_active = parse_bool(
            data.get("is_active"),
            default=item.is_active
        )

    try:

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Menu item updated successfully.",
            "item": menu_item_to_dict(item)
        }), 200

    except Exception as exc:

        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to update menu item.",
            "error": str(exc)
        }), 500


# =========================================================
# DELETE MENU ITEM
# =========================================================

@admin_menu_items_bp.route(
    "/<int:item_id>",
    methods=["DELETE"]
)
def delete_menu_item(item_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    item = MenuItem.query.get(item_id)

    if not item:
        return jsonify({
            "success": False,
            "message": "Menu item not found."
        }), 404

    try:

        db.session.delete(item)

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Menu item deleted successfully."
        }), 200

    except Exception as exc:

        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to delete menu item.",
            "error": str(exc)
        }), 500


# =========================================================
# ACTIVATE
# =========================================================

@admin_menu_items_bp.route(
    "/<int:item_id>/activate",
    methods=["POST"]
)
def activate_menu_item(item_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    item = MenuItem.query.get(item_id)

    if not item:
        return jsonify({
            "success": False,
            "message": "Menu item not found."
        }), 404

    try:

        item.is_active = True

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Menu item activated.",
            "item": menu_item_to_dict(item)
        }), 200

    except Exception as exc:

        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to activate menu item.",
            "error": str(exc)
        }), 500


# =========================================================
# DEACTIVATE
# =========================================================

@admin_menu_items_bp.route(
    "/<int:item_id>/deactivate",
    methods=["POST"]
)
def deactivate_menu_item(item_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    item = MenuItem.query.get(item_id)

    if not item:
        return jsonify({
            "success": False,
            "message": "Menu item not found."
        }), 404

    try:

        item.is_active = False

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Menu item deactivated.",
            "item": menu_item_to_dict(item)
        }), 200

    except Exception as exc:

        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to deactivate menu item.",
            "error": str(exc)
        }), 500


# =========================================================
# REORDER MENU ITEMS
# =========================================================
#
# Expected JSON:
#
# {
#     "menu_id": 1,
#     "items": [
#         {"id": 5, "position": 0},
#         {"id": 2, "position": 1},
#         {"id": 8, "position": 2}
#     ]
# }
#
# =========================================================

@admin_menu_items_bp.route(
    "/reorder",
    methods=["POST", "PUT"]
)
def reorder_menu_items():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}

    menu_id = parse_int(
        data.get("menu_id"),
        default=None,
        minimum=1
    )

    items = data.get("items")

    if not menu_id:

        return jsonify({
            "success": False,
            "message": "menu_id is required."
        }), 400

    if not isinstance(items, list) or not items:

        return jsonify({
            "success": False,
            "message": "items must be a non-empty list."
        }), 400

    menu = Menu.query.get(menu_id)

    if not menu:

        return jsonify({
            "success": False,
            "message": "Menu not found."
        }), 404

    # -----------------------------------------------------
    # VALIDATE ALL ITEMS FIRST
    # -----------------------------------------------------

    updates = []

    seen_ids = set()

    seen_positions = set()

    for entry in items:

        if not isinstance(entry, dict):

            return jsonify({
                "success": False,
                "message": "Each reorder item must be an object."
            }), 400

        item_id = parse_int(
            entry.get("id"),
            default=None,
            minimum=1
        )

        position = parse_int(
            entry.get("position"),
            default=None,
            minimum=0
        )

        if not item_id or position is None:

            return jsonify({
                "success": False,
                "message": "Each item requires id and position."
            }), 400

        if item_id in seen_ids:

            return jsonify({
                "success": False,
                "message": "Duplicate item id in reorder request."
            }), 400

        if position in seen_positions:

            return jsonify({
                "success": False,
                "message": "Duplicate position in reorder request."
            }), 400

        seen_ids.add(item_id)

        seen_positions.add(position)

        item = MenuItem.query.get(item_id)

        if not item:

            return jsonify({
                "success": False,
                "message": f"Menu item {item_id} not found."
            }), 404

        if item.menu_id != menu_id:

            return jsonify({
                "success": False,
                "message": (
                    f"Menu item {item_id} does not "
                    f"belong to menu {menu_id}."
                )
            }), 400

        updates.append(
            (item, position)
        )

    # -----------------------------------------------------
    # UPDATE POSITIONS
    # -----------------------------------------------------

    try:

        for item, position in updates:
            item.position = position

        db.session.commit()

        updated_items = (
            MenuItem.query
            .filter_by(menu_id=menu_id)
            .order_by(
                MenuItem.position.asc(),
                MenuItem.id.asc()
            )
            .all()
        )

        return jsonify({
            "success": True,
            "message": "Menu items reordered successfully.",
            "items": [
                menu_item_to_dict(item)
                for item in updated_items
            ]
        }), 200

    except Exception as exc:

        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to reorder menu items.",
            "error": str(exc)
        }), 500


# =========================================================
# GET MENU ITEMS BY MENU
# =========================================================

@admin_menu_items_bp.route(
    "/menu/<int:menu_id>",
    methods=["GET"]
)
def get_items_by_menu(menu_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    menu = Menu.query.get(menu_id)

    if not menu:

        return jsonify({
            "success": False,
            "message": "Menu not found."
        }), 404

    items = (
        MenuItem.query
        .filter_by(menu_id=menu_id)
        .order_by(
            MenuItem.position.asc(),
            MenuItem.id.asc()
        )
        .all()
    )

    return jsonify({
        "success": True,
        "menu": {
            "id": menu.id,
            "name": menu.name,
            "location": menu.location,
            "is_active": bool(menu.is_active),
        },
        "count": len(items),
        "items": [
            menu_item_to_dict(item)
            for item in items
        ]
    }), 200


# =========================================================
# SUMMARY
# =========================================================

@admin_menu_items_bp.route(
    "/summary",
    methods=["GET"]
)
def menu_items_summary():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        total = MenuItem.query.count()

        active = (
            MenuItem.query
            .filter_by(is_active=True)
            .count()
        )

        inactive = (
            MenuItem.query
            .filter_by(is_active=False)
            .count()
        )

        custom_urls = (
            MenuItem.query
            .filter_by(item_type="custom_url")
            .count()
        )

        pages = (
            MenuItem.query
            .filter_by(item_type="page")
            .count()
        )

        books = (
            MenuItem.query
            .filter_by(item_type="book")
            .count()
        )

        categories = (
            MenuItem.query
            .filter_by(item_type="category")
            .count()
        )

        home = (
            MenuItem.query
            .filter_by(item_type="home")
            .count()
        )

        books_page = (
            MenuItem.query
            .filter_by(item_type="books")
            .count()
        )

        search_page = (
            MenuItem.query
            .filter_by(item_type="search")
            .count()
        )

        return jsonify({
            "success": True,

            "stats": {
                "total": total,
                "active": active,
                "inactive": inactive,

                "custom_url": custom_urls,
                "page": pages,
                "book": books,
                "category": categories,
                "home": home,
                "books": books_page,
                "search": search_page,
            }
        }), 200

    except Exception as exc:

        return jsonify({
            "success": False,
            "message": "Failed to load menu item summary.",
            "error": str(exc)
        }), 500
