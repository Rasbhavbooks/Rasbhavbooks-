# ============================================================
# RASBHAV BOOKS
# ADMIN CATEGORY ROUTES / API
# ============================================================
#
# ADMIN PANEL
#      ↓
# CATEGORY API
#      ↓
# DATABASE
#      ↓
# PUBLIC WEBSITE
#
# Features:
# - Admin authentication
# - Category CRUD
# - Search
# - Slug validation
# - Parent / Child categories
# - Circular hierarchy protection
# - Category image
# - Book mapping
# - Category hierarchy
# - Safe delete protection
# - Strict validation
# - Safe JSON responses
# - Database rollback
# ============================================================


from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from app import db

from app.models.category import Category
from app.models.book import Book
from app.models.book_categories import BookCategory

from app.routes.admin import admin_required


# ============================================================
# BLUEPRINT
# ============================================================

admin_categories_bp = Blueprint(
    "admin_categories",
    __name__,
    url_prefix="/api/admin/categories"
)


# ============================================================
# HELPERS
# ============================================================

def clean_string(value, default=None):
    """
    Convert a value into a trimmed string.

    Empty values return default.
    """

    if value is None:
        return default

    value = str(value).strip()

    if not value:
        return default

    return value


def parse_int(value, default=None):
    """
    Safely convert value to integer.
    """

    if value is None:
        return default

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def parse_optional_parent_id(value):
    """
    Parse parent_id safely.

    Allowed:
    - None
    - ""
    - whitespace
    - integer
    - numeric string

    Invalid non-empty values raise ValueError.
    """

    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()

        if not value:
            return None

    parsed = parse_int(value)

    if parsed is None:
        raise ValueError(
            "Invalid parent_id."
        )

    if parsed < 1:
        raise ValueError(
            "Invalid parent_id."
        )

    return parsed


# ============================================================
# CATEGORY SERIALIZER
# ============================================================

def category_to_dict(category, include_books=False):
    """
    Convert Category model into safe JSON dictionary.
    """

    parent_data = None

    if category.parent:

        parent_data = {
            "id": category.parent.id,
            "name": category.parent.name,
            "slug": category.parent.slug
        }

    children = []

    for child in sorted(
        category.children,
        key=lambda item: (
            item.name or ""
        ).lower()
    ):

        children.append({
            "id": child.id,
            "name": child.name,
            "slug": child.slug,
            "parent_id": child.parent_id
        })

    data = {

        "id":
            category.id,

        "name":
            category.name,

        "slug":
            category.slug,

        "description":
            category.description,

        "image":
            category.image,

        "parent_id":
            category.parent_id,

        "parent":
            parent_data,

        "children":
            children,

        "is_parent":
            len(children) > 0,

        "has_parent":
            category.parent_id is not None,

        "full_name":
            category.get_full_name(),

        "created_at": (
            category.created_at.isoformat()
            if category.created_at
            else None
        ),

        "updated_at": (
            category.updated_at.isoformat()
            if category.updated_at
            else None
        )
    }

    # --------------------------------------------------------
    # BOOKS
    # --------------------------------------------------------

    if include_books:

        books = (
            Book.query
            .join(
                BookCategory,
                BookCategory.book_id == Book.id
            )
            .filter(
                BookCategory.category_id == category.id
            )
            .order_by(
                Book.title.asc()
            )
            .all()
        )

        data["books"] = [

            {
                "id":
                    book.id,

                "title":
                    book.title,

                "slug":
                    book.slug,

                "published":
                    bool(book.published),

                "featured":
                    bool(book.featured),

                "cover_image":
                    book.cover_image
            }

            for book in books
        ]

        data["book_count"] = len(
            books
        )

    return data


# ============================================================
# CATEGORY HIERARCHY SERIALIZER
# ============================================================

def hierarchy_item(category, visited=None):
    """
    Recursively serialize category hierarchy.

    visited prevents infinite recursion if bad database
    data somehow exists.
    """

    if visited is None:
        visited = set()

    if category.id in visited:

        return {
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "description": category.description,
            "image": category.image,
            "parent_id": category.parent_id,
            "children": []
        }

    visited = visited | {
        category.id
    }

    children = []

    for child in sorted(
        category.children,
        key=lambda item: (
            item.name or ""
        ).lower()
    ):

        children.append(
            hierarchy_item(
                child,
                visited
            )
        )

    return {

        "id":
            category.id,

        "name":
            category.name,

        "slug":
            category.slug,

        "description":
            category.description,

        "image":
            category.image,

        "parent_id":
            category.parent_id,

        "children":
            children
    }


# ============================================================
# CHECK CIRCULAR PARENT
# ============================================================

def creates_circular_relation(
    category,
    parent_id
):
    """
    Check whether assigning parent_id would create
    a circular hierarchy.
    """

    if parent_id is None:
        return False

    if parent_id == category.id:
        return True

    visited = set()

    current_id = parent_id

    while current_id is not None:

        if current_id in visited:
            return True

        visited.add(
            current_id
        )

        if current_id == category.id:
            return True

        current = Category.query.get(
            current_id
        )

        if not current:
            return False

        current_id = current.parent_id

    return False


# ============================================================
# VALIDATE PARENT
# ============================================================

def validate_parent(
    parent_id,
    category=None
):
    """
    Validate parent category.

    Returns:
        Category object or None
    """

    parent_id = parse_optional_parent_id(
        parent_id
    )

    if parent_id is None:
        return None

    if category:

        if parent_id == category.id:

            raise ValueError(
                "A category cannot be its own parent."
            )

        if creates_circular_relation(
            category,
            parent_id
        ):

            raise ValueError(
                "Circular category hierarchy is not allowed."
            )

    parent = Category.query.get(
        parent_id
    )

    if not parent:

        raise LookupError(
            "Parent category not found."
        )

    return parent


# ============================================================
# NORMALIZE BOOK IDS
# ============================================================

def normalize_book_ids(value):
    """
    Convert book IDs into a unique integer list.

    Supported:
        [1, 2, 3]
        "1,2,3"
        1
        "1"
    """

    if value is None:
        return []

    if isinstance(value, str):

        value = value.strip()

        if not value:
            return []

        value = [
            item.strip()
            for item in value.split(",")
        ]

    if not isinstance(value, list):

        value = [
            value
        ]

    result = []

    for item in value:

        if isinstance(item, str):

            item = item.strip()

            if not item:
                continue

        book_id = parse_int(
            item
        )

        if book_id is None:

            raise ValueError(
                f"Invalid book_id: {item}"
            )

        if book_id < 1:

            raise ValueError(
                f"Invalid book_id: {item}"
            )

        if book_id not in result:

            result.append(
                book_id
            )

    return result


# ============================================================
# VALIDATE BOOK IDS
# ============================================================

def validate_books(book_ids):
    """
    Make sure every requested book exists.
    """

    if not book_ids:
        return []

    books = (
        Book.query
        .filter(
            Book.id.in_(book_ids)
        )
        .all()
    )

    found_ids = {
        book.id
        for book in books
    }

    missing = [

        book_id

        for book_id in book_ids

        if book_id not in found_ids
    ]

    if missing:

        raise LookupError(
            "Book not found: "
            + ", ".join(
                str(item)
                for item in missing
            )
        )

    return books


# ============================================================
# UPDATE CATEGORY BOOKS
# ============================================================

def update_category_books(
    category,
    book_ids
):
    """
    Replace complete book mapping for a category.
    """

    book_ids = normalize_book_ids(
        book_ids
    )

    validate_books(
        book_ids
    )

    # --------------------------------------------------------
    # REMOVE OLD RELATIONS
    # --------------------------------------------------------

    BookCategory.query.filter_by(
        category_id=category.id
    ).delete(
        synchronize_session=False
    )

    # --------------------------------------------------------
    # CREATE NEW RELATIONS
    # --------------------------------------------------------

    for book_id in book_ids:

        relation = BookCategory(

            book_id=book_id,

            category_id=category.id

        )

        db.session.add(
            relation
        )


# ============================================================
# GET ALL CATEGORIES
# ============================================================

@admin_categories_bp.route(
    "",
    methods=["GET"]
)
@admin_categories_bp.route(
    "/",
    methods=["GET"]
)
def get_categories():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        query = Category.query

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
                or_(
                    Category.name.ilike(
                        pattern
                    ),
                    Category.slug.ilike(
                        pattern
                    ),
                    Category.description.ilike(
                        pattern
                    )
                )
            )

        # ----------------------------------------------------
        # PARENT FILTER
        # ----------------------------------------------------

        if "parent_id" in request.args:

            raw_parent_id = request.args.get(
                "parent_id"
            )

            parent_id = parse_optional_parent_id(
                raw_parent_id
            )

            if parent_id is None:

                query = query.filter(
                    Category.parent_id.is_(None)
                )

            else:

                query = query.filter(
                    Category.parent_id == parent_id
                )

        # ----------------------------------------------------
        # LIMIT
        # ----------------------------------------------------

        limit = parse_int(
            request.args.get(
                "limit"
            ),
            200
        )

        if limit is None:
            limit = 200

        if limit < 1:
            limit = 1

        if limit > 500:
            limit = 500

        # ----------------------------------------------------
        # LOAD
        # ----------------------------------------------------

        categories = (
            query
            .order_by(
                Category.name.asc()
            )
            .limit(limit)
            .all()
        )

        return jsonify({

            "success":
                True,

            "count":
                len(categories),

            "categories": [

                category_to_dict(
                    category
                )

                for category in categories
            ]

        }), 200

    except ValueError as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                str(error)

        }), 400

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load categories.",

            "error":
                str(error)

        }), 500


# ============================================================
# GET CATEGORY HIERARCHY
# ============================================================

@admin_categories_bp.route(
    "/hierarchy",
    methods=["GET"]
)
def get_category_hierarchy():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        categories = (
            Category.query
            .filter(
                Category.parent_id.is_(None)
            )
            .order_by(
                Category.name.asc()
            )
            .all()
        )

        return jsonify({

            "success":
                True,

            "count":
                len(categories),

            "categories": [

                hierarchy_item(
                    category
                )

                for category in categories
            ]

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load category hierarchy.",

            "error":
                str(error)

        }), 500


# ============================================================
# GET SINGLE CATEGORY
# ============================================================

@admin_categories_bp.route(
    "/<int:category_id>",
    methods=["GET"]
)
def get_category(category_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        category = Category.query.get(
            category_id
        )

        if not category:

            return jsonify({

                "success":
                    False,

                "message":
                    "Category not found."

            }), 404

        return jsonify({

            "success":
                True,

            "category":
                category_to_dict(
                    category,
                    include_books=True
                )

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load category.",

            "error":
                str(error)

        }), 500


# ============================================================
# GET CATEGORY BOOKS
# ============================================================

@admin_categories_bp.route(
    "/<int:category_id>/books",
    methods=["GET"]
)
def get_category_books(category_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        category = Category.query.get(
            category_id
        )

        if not category:

            return jsonify({

                "success":
                    False,

                "message":
                    "Category not found."

            }), 404

        books = (
            Book.query
            .join(
                BookCategory,
                BookCategory.book_id == Book.id
            )
            .filter(
                BookCategory.category_id == category.id
            )
            .order_by(
                Book.title.asc()
            )
            .all()
        )

        return jsonify({

            "success":
                True,

            "category": {

                "id":
                    category.id,

                "name":
                    category.name,

                "slug":
                    category.slug
            },

            "count":
                len(books),

            "books": [

                {
                    "id":
                        book.id,

                    "title":
                        book.title,

                    "slug":
                        book.slug,

                    "published":
                        bool(book.published),

                    "featured":
                        bool(book.featured),

                    "cover_image":
                        book.cover_image
                }

                for book in books
            ]

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load category books.",

            "error":
                str(error)

        }), 500


# ============================================================
# CREATE CATEGORY
# ============================================================

@admin_categories_bp.route(
    "",
    methods=["POST"]
)
@admin_categories_bp.route(
    "/",
    methods=["POST"]
)
def create_category():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(
        silent=True
    ) or {}

    try:

        # ----------------------------------------------------
        # NAME
        # ----------------------------------------------------

        name = clean_string(
            data.get("name")
        )

        if not name:

            return jsonify({

                "success":
                    False,

                "message":
                    "Category name is required."

            }), 400

        # ----------------------------------------------------
        # SLUG
        # ----------------------------------------------------

        slug = clean_string(
            data.get("slug")
        )

        if not slug:

            return jsonify({

                "success":
                    False,

                "message":
                    "Category slug is required."

            }), 400

        existing = (
            Category.query
            .filter_by(
                slug=slug
            )
            .first()
        )

        if existing:

            return jsonify({

                "success":
                    False,

                "message":
                    "Category slug already exists."

            }), 409

        # ----------------------------------------------------
        # PARENT
        # ----------------------------------------------------

        parent_id = parse_optional_parent_id(
            data.get("parent_id")
        )

        validate_parent(
            parent_id
        )

        # ----------------------------------------------------
        # CREATE
        # ----------------------------------------------------

        category = Category(

            name=name,

            slug=slug,

            description=clean_string(
                data.get(
                    "description"
                )
            ),

            image=clean_string(
                data.get(
                    "image"
                )
            ),

            parent_id=parent_id
        )

        db.session.add(
            category
        )

        db.session.flush()

        # ----------------------------------------------------
        # BOOK MAPPING
        # ----------------------------------------------------

        if "book_ids" in data:

            update_category_books(
                category,
                data.get(
                    "book_ids"
                )
            )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Category created successfully.",

            "category":
                category_to_dict(
                    category,
                    include_books=True
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

    except IntegrityError:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Category could not be created because of a database constraint."

        }), 409

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to create category.",

            "error":
                str(error)

        }), 500


# ============================================================
# UPDATE CATEGORY
# ============================================================

@admin_categories_bp.route(
    "/<int:category_id>",
    methods=["PUT", "PATCH"]
)
def update_category(category_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(
        silent=True
    ) or {}

    try:

        category = Category.query.get(
            category_id
        )

        if not category:

            return jsonify({

                "success":
                    False,

                "message":
                    "Category not found."

            }), 404

        # ----------------------------------------------------
        # NAME
        # ----------------------------------------------------

        if "name" in data:

            name = clean_string(
                data.get("name")
            )

            if not name:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Category name cannot be empty."

                }), 400

            category.name = name

        # ----------------------------------------------------
        # SLUG
        # ----------------------------------------------------

        if "slug" in data:

            slug = clean_string(
                data.get("slug")
            )

            if not slug:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Category slug cannot be empty."

                }), 400

            existing = (
                Category.query
                .filter(
                    Category.slug == slug,
                    Category.id != category.id
                )
                .first()
            )

            if existing:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Category slug already exists."

                }), 409

            category.slug = slug

        # ----------------------------------------------------
        # DESCRIPTION
        # ----------------------------------------------------

        if "description" in data:

            category.description = clean_string(
                data.get(
                    "description"
                )
            )

        # ----------------------------------------------------
        # IMAGE
        # ----------------------------------------------------

        if "image" in data:

            category.image = clean_string(
                data.get(
                    "image"
                )
            )

        # ----------------------------------------------------
        # PARENT
        # ----------------------------------------------------

        if "parent_id" in data:

            parent_id = parse_optional_parent_id(
                data.get(
                    "parent_id"
                )
            )

            validate_parent(
                parent_id,
                category
            )

            category.parent_id = parent_id

        # ----------------------------------------------------
        # BOOKS
        # ----------------------------------------------------

        if "book_ids" in data:

            update_category_books(
                category,
                data.get(
                    "book_ids"
                )
            )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Category updated successfully.",

            "category":
                category_to_dict(
                    category,
                    include_books=True
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

    except IntegrityError:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Category could not be updated because of a database constraint."

        }), 409

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to update category.",

            "error":
                str(error)

        }), 500


# ============================================================
# DELETE CATEGORY
# ============================================================

@admin_categories_bp.route(
    "/<int:category_id>",
    methods=["DELETE"]
)
def delete_category(category_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        category = Category.query.get(
            category_id
        )

        if not category:

            return jsonify({

                "success":
                    False,

                "message":
                    "Category not found."

            }), 404

        # ----------------------------------------------------
        # SAFE CHILD CHECK
        # ----------------------------------------------------
        #
        # IMPORTANT:
        # Category model has delete-orphan cascade on children.
        # Therefore we DO NOT delete a parent category while
        # children exist.
        #
        # This prevents accidental deletion of the hierarchy.
        # ----------------------------------------------------

        children = (
            Category.query
            .filter_by(
                parent_id=category.id
            )
            .all()
        )

        if children:

            return jsonify({

                "success":
                    False,

                "message":
                    "Cannot delete this category because it has child categories.",

                "child_count":
                    len(children),

                "children": [

                    {
                        "id":
                            child.id,

                        "name":
                            child.name,

                        "slug":
                            child.slug

                    }

                    for child in children
                ]

            }), 409

        # ----------------------------------------------------
        # DELETE BOOK RELATIONS
        # ----------------------------------------------------

        BookCategory.query.filter_by(
            category_id=category.id
        ).delete(
            synchronize_session=False
        )

        # ----------------------------------------------------
        # DELETE CATEGORY
        # ----------------------------------------------------

        db.session.delete(
            category
        )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Category deleted successfully.",

            "category_id":
                category_id

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to delete category.",

            "error":
                str(error)

        }), 500


# ============================================================
# SET CATEGORY BOOKS
# ============================================================

@admin_categories_bp.route(
    "/<int:category_id>/books",
    methods=["PUT", "POST"]
)
def set_category_books(category_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(
        silent=True
    ) or {}

    try:

        category = Category.query.get(
            category_id
        )

        if not category:

            return jsonify({

                "success":
                    False,

                "message":
                    "Category not found."

            }), 404

        book_ids = data.get(
            "book_ids",
            []
        )

        update_category_books(
            category,
            book_ids
        )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Category books updated successfully.",

            "category":
                category_to_dict(
                    category,
                    include_books=True
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
                "Unable to update category books.",

            "error":
                str(error)

        }), 500
