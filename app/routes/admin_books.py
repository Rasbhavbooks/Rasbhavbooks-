# ============================================================
# RASBHAV BOOKS
# ADMIN BOOK ROUTES / API
# ============================================================
#
# ADMIN PANEL
#      ↓
# ADMIN BOOK API
#      ↓
# DATABASE
#      ↓
# PUBLIC WEBSITE
#
# Features:
# - Admin authentication
# - Book CRUD
# - Slug validation
# - Author support
# - Category support
# - Publish / Draft
# - Featured control
# - Publish date
# - SEO management
# - JSON-LD Book Schema
# - Safe JSON responses
# - Database rollback
# ============================================================


from flask import Blueprint, request, jsonify

from datetime import datetime
import json

from app import db

from app.models.book import Book
from app.models.seo import SEO
from app.models.author import Author
from app.models.category import Category
from app.models.book_categories import BookCategory

from app.routes.admin import admin_required


# ============================================================
# BLUEPRINT
# ============================================================

admin_books_bp = Blueprint(
    "admin_books",
    __name__,
    url_prefix="/api/admin/books"
)


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


def parse_bool(value, default=False):
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        return bool(value)

    if isinstance(value, str):

        value = value.strip().lower()

        if value in (
            "true",
            "1",
            "yes",
            "on",
            "enabled"
        ):
            return True

        if value in (
            "false",
            "0",
            "no",
            "off",
            "disabled"
        ):
            return False

    return default


def parse_int(value, default=None):
    if value is None:
        return default

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def parse_datetime(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value

    try:
        return datetime.fromisoformat(
            str(value).replace(
                "Z",
                "+00:00"
            )
        )

    except (
        ValueError,
        TypeError
    ):
        raise ValueError(
            "Invalid publish_date format."
        )


# ============================================================
# AUTHOR VALIDATION
# ============================================================

def validate_author(author_id):
    if author_id is None:
        return None

    author_id = parse_int(author_id)

    if author_id is None:
        raise ValueError(
            "Invalid author_id."
        )

    author = Author.query.get(author_id)

    if not author:
        raise ValueError(
            "Author not found."
        )

    return author


# ============================================================
# CATEGORY VALIDATION
# ============================================================

def normalize_category_ids(value):
    if value is None:
        return []

    if isinstance(value, str):

        value = value.strip()

        if not value:
            return []

        try:
            value = json.loads(value)

        except (
            ValueError,
            TypeError,
            json.JSONDecodeError
        ):
            value = [
                item.strip()
                for item in value.split(",")
                if item.strip()
            ]

    if not isinstance(value, list):
        value = [value]

    result = []

    for item in value:

        category_id = parse_int(item)

        if category_id is None:
            continue

        if category_id not in result:
            result.append(category_id)

    return result


def validate_categories(category_ids):

    if not category_ids:
        return []

    categories = (
        Category.query
        .filter(
            Category.id.in_(category_ids)
        )
        .all()
    )

    found_ids = {
        category.id
        for category in categories
    }

    missing_ids = [
        category_id
        for category_id in category_ids
        if category_id not in found_ids
    ]

    if missing_ids:
        raise ValueError(
            "Category not found: "
            + ", ".join(
                str(item)
                for item in missing_ids
            )
        )

    return categories


# ============================================================
# SEO SCHEMA
# ============================================================

def build_book_schema(book):

    description = (
        book.short_description
        or book.description
        or f"Read {book.title} online on Rasbhav Books."
    )

    schema = {
        "@context": "https://schema.org",
        "@type": "Book",
        "name": book.title,
        "url": f"/books/{book.slug}",
        "description": description
    }

    if book.cover_image:
        schema["image"] = book.cover_image

    if book.language:
        schema["inLanguage"] = book.language

    if book.author:
        schema["author"] = {
            "@type": "Person",
            "name": book.author.name
        }

    return schema


# ============================================================
# SEO SAVE
# ============================================================

def save_book_seo(book, data):

    seo = (
        SEO.query
        .filter_by(
            entity_type="book",
            entity_id=book.id
        )
        .first()
    )

    if not seo:

        seo = SEO(
            entity_type="book",
            entity_id=book.id
        )

        db.session.add(seo)

    description = (
        book.short_description
        or book.description
        or f"Read {book.title} online on Rasbhav Books."
    )

    default_title = (
        f"{book.title} | Rasbhav Books"
    )

    default_canonical = (
        f"/books/{book.slug}"
    )

    # --------------------------------------------------------
    # META TITLE
    # --------------------------------------------------------

    if "meta_title" in data:

        seo.meta_title = clean_string(
            data.get("meta_title"),
            default_title
        )

    elif not seo.meta_title:

        seo.meta_title = default_title

    # --------------------------------------------------------
    # META DESCRIPTION
    # --------------------------------------------------------

    if "meta_description" in data:

        seo.meta_description = clean_string(
            data.get("meta_description"),
            description
        )

    elif not seo.meta_description:

        seo.meta_description = description

    # --------------------------------------------------------
    # FOCUS KEYWORD
    # --------------------------------------------------------

    if "focus_keyword" in data:

        seo.focus_keyword = clean_string(
            data.get("focus_keyword"),
            book.title
        )

    elif not seo.focus_keyword:

        seo.focus_keyword = book.title

    # --------------------------------------------------------
    # CANONICAL
    # --------------------------------------------------------

    if "canonical_url" in data:

        seo.canonical_url = clean_string(
            data.get("canonical_url"),
            default_canonical
        )

    elif not seo.canonical_url:

        seo.canonical_url = default_canonical

    # --------------------------------------------------------
    # ROBOTS
    # --------------------------------------------------------

    if "robots" in data:

        seo.robots = clean_string(
            data.get("robots"),
            "index, follow"
        )

    elif not seo.robots:

        seo.robots = "index, follow"

    # --------------------------------------------------------
    # OPEN GRAPH TITLE
    # --------------------------------------------------------

    if "og_title" in data:

        seo.og_title = clean_string(
            data.get("og_title"),
            seo.meta_title
        )

    elif not seo.og_title:

        seo.og_title = seo.meta_title

    # --------------------------------------------------------
    # OPEN GRAPH DESCRIPTION
    # --------------------------------------------------------

    if "og_description" in data:

        seo.og_description = clean_string(
            data.get("og_description"),
            seo.meta_description
        )

    elif not seo.og_description:

        seo.og_description = seo.meta_description

    # --------------------------------------------------------
    # OPEN GRAPH IMAGE
    # --------------------------------------------------------

    if "og_image" in data:

        seo.og_image = clean_string(
            data.get("og_image"),
            book.cover_image
        )

    elif not seo.og_image:

        seo.og_image = book.cover_image

    # --------------------------------------------------------
    # JSON-LD
    # --------------------------------------------------------

    if "schema_data" in data:

        schema_data = data.get(
            "schema_data"
        )

        if schema_data:

            if isinstance(
                schema_data,
                str
            ):

                try:

                    parsed_schema = json.loads(
                        schema_data
                    )

                except (
                    ValueError,
                    TypeError,
                    json.JSONDecodeError
                ):

                    raise ValueError(
                        "Invalid schema_data JSON."
                    )

                seo.schema_data = json.dumps(
                    parsed_schema,
                    ensure_ascii=False
                )

            elif isinstance(
                schema_data,
                (dict, list)
            ):

                seo.schema_data = json.dumps(
                    schema_data,
                    ensure_ascii=False
                )

            else:

                raise ValueError(
                    "schema_data must be valid JSON."
                )

        else:

            seo.schema_data = json.dumps(
                build_book_schema(book),
                ensure_ascii=False
            )

    else:

        seo.schema_data = json.dumps(
            build_book_schema(book),
            ensure_ascii=False
        )

    return seo


# ============================================================
# SEO SERIALIZER
# ============================================================

def seo_to_dict(seo):

    if not seo:
        return None

    return {

        "id": seo.id,

        "entity_type":
            seo.entity_type,

        "entity_id":
            seo.entity_id,

        "meta_title":
            seo.meta_title,

        "meta_description":
            seo.meta_description,

        "focus_keyword":
            seo.focus_keyword,

        "canonical_url":
            seo.canonical_url,

        "robots":
            seo.robots,

        "og_title":
            seo.og_title,

        "og_description":
            seo.og_description,

        "og_image":
            seo.og_image,

        "schema_data":
            seo.schema_data,

        "created_at": (
            seo.created_at.isoformat()
            if seo.created_at
            else None
        ),

        "updated_at": (
            seo.updated_at.isoformat()
            if seo.updated_at
            else None
        )
    }


# ============================================================
# CATEGORY SERIALIZER
# ============================================================

def category_to_dict(category):

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
            category.parent_id
    }


# ============================================================
# BOOK SERIALIZER
# ============================================================

def book_to_dict(book):

    categories = []

    try:

        categories = [
            category_to_dict(category)
            for category in book.categories
        ]

    except Exception:

        categories = []

    seo = (
        SEO.query
        .filter_by(
            entity_type="book",
            entity_id=book.id
        )
        .first()
    )

    author_data = None

    if book.author:

        author_data = {

            "id":
                book.author.id,

            "name":
                book.author.name,

            "slug":
                book.author.slug,

            "profile_image":
                book.author.profile_image
        }

    return {

        "id":
            book.id,

        "title":
            book.title,

        "slug":
            book.slug,

        "subtitle":
            book.subtitle,

        "description":
            book.description,

        "short_description":
            book.short_description,

        "author_id":
            book.author_id,

        "author":
            author_data,

        "language":
            book.language,

        "tags":
            book.tags,

        "cover_image":
            book.cover_image,

        "banner_image":
            book.banner_image,

        "featured_image":
            book.featured_image,

        "status":
            book.status,

        "featured":
            bool(book.featured),

        "published":
            bool(book.published),

        "publish_date": (
            book.publish_date.isoformat()
            if book.publish_date
            else None
        ),

        "categories":
            categories,

        "category_ids": [
            category["id"]
            for category in categories
        ],

        "seo":
            seo_to_dict(seo),

        "created_at": (
            book.created_at.isoformat()
            if book.created_at
            else None
        ),

        "updated_at": (
            book.updated_at.isoformat()
            if book.updated_at
            else None
        )
    }


# ============================================================
# UPDATE BOOK CATEGORIES
# ============================================================

def update_book_categories(
    book,
    category_ids
):

    category_ids = normalize_category_ids(
        category_ids
    )

    categories = validate_categories(
        category_ids
    )

    BookCategory.query.filter_by(
        book_id=book.id
    ).delete(
        synchronize_session=False
    )

    for category in categories:

        relation = BookCategory(
            book_id=book.id,
            category_id=category.id
        )

        db.session.add(
            relation
        )

    return categories


# ============================================================
# GET ALL BOOKS
# ============================================================

@admin_books_bp.route(
    "",
    methods=["GET"]
)
@admin_books_bp.route(
    "/",
    methods=["GET"]
)
def get_books():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        query = Book.query

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
                    Book.title.ilike(pattern),
                    Book.slug.ilike(pattern),
                    Book.description.ilike(pattern),
                    Book.short_description.ilike(pattern),
                    Book.language.ilike(pattern),
                    Book.tags.ilike(pattern)
                )
            )

        # ----------------------------------------------------
        # STATUS FILTER
        # ----------------------------------------------------

        status = clean_string(
            request.args.get("status")
        )

        if status:

            query = query.filter(
                Book.status == status
            )

        # ----------------------------------------------------
        # PUBLISHED FILTER
        # ----------------------------------------------------

        if "published" in request.args:

            published = parse_bool(
                request.args.get(
                    "published"
                )
            )

            query = query.filter(
                Book.published == published
            )

        # ----------------------------------------------------
        # FEATURED FILTER
        # ----------------------------------------------------

        if "featured" in request.args:

            featured = parse_bool(
                request.args.get(
                    "featured"
                )
            )

            query = query.filter(
                Book.featured == featured
            )

        # ----------------------------------------------------
        # LIMIT
        # ----------------------------------------------------

        limit = parse_int(
            request.args.get(
                "limit"
            ),
            50
        )

        if limit < 1:
            limit = 1

        if limit > 200:
            limit = 200

        books = (
            query
            .order_by(
                Book.created_at.desc()
            )
            .limit(limit)
            .all()
        )

        return jsonify({

            "success":
                True,

            "count":
                len(books),

            "books": [
                book_to_dict(book)
                for book in books
            ]

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load books.",

            "error":
                str(error)

        }), 500


# ============================================================
# GET SINGLE BOOK
# ============================================================

@admin_books_bp.route(
    "/<int:book_id>",
    methods=["GET"]
)
def get_book(book_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        book = Book.query.get(
            book_id
        )

        if not book:

            return jsonify({

                "success":
                    False,

                "message":
                    "Book not found."

            }), 404

        return jsonify({

            "success":
                True,

            "book":
                book_to_dict(book)

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load book.",

            "error":
                str(error)

        }), 500


# ============================================================
# CREATE BOOK
# ============================================================

@admin_books_bp.route(
    "",
    methods=["POST"]
)
@admin_books_bp.route(
    "/",
    methods=["POST"]
)
def create_book():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(
        silent=True
    ) or {}

    try:

        # ----------------------------------------------------
        # REQUIRED
        # ----------------------------------------------------

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
                    "Book title is required."

            }), 400

        if not slug:

            return jsonify({

                "success":
                    False,

                "message":
                    "Book slug is required."

            }), 400

        # ----------------------------------------------------
        # SLUG UNIQUE
        # ----------------------------------------------------

        existing = (
            Book.query
            .filter_by(slug=slug)
            .first()
        )

        if existing:

            return jsonify({

                "success":
                    False,

                "message":
                    "Book slug already exists."

            }), 409

        # ----------------------------------------------------
        # AUTHOR
        # ----------------------------------------------------

        author_id = data.get(
            "author_id"
        )

        validate_author(
            author_id
        )

        # ----------------------------------------------------
        # CATEGORIES
        # ----------------------------------------------------

        category_ids = normalize_category_ids(
            data.get("category_ids")
        )

        validate_categories(
            category_ids
        )

        # ----------------------------------------------------
        # PUBLISH DATE
        # ----------------------------------------------------

        publish_date = parse_datetime(
            data.get("publish_date")
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        status = clean_string(
            data.get("status"),
            "draft"
        )

        allowed_statuses = (
            "draft",
            "published",
            "private"
        )

        if status not in allowed_statuses:

            return jsonify({

                "success":
                    False,

                "message":
                    "Invalid book status."

            }), 400

        published = parse_bool(
            data.get("published"),
            status == "published"
        )

        # ----------------------------------------------------
        # CREATE
        # ----------------------------------------------------

        book = Book(

            title=title,

            slug=slug,

            subtitle=clean_string(
                data.get("subtitle")
            ),

            description=clean_string(
                data.get("description")
            ),

            short_description=clean_string(
                data.get("short_description")
            ),

            author_id=(
                parse_int(author_id)
                if author_id is not None
                else None
            ),

            language=clean_string(
                data.get("language")
            ),

            tags=clean_string(
                data.get("tags")
            ),

            cover_image=clean_string(
                data.get("cover_image")
            ),

            banner_image=clean_string(
                data.get("banner_image")
            ),

            featured_image=clean_string(
                data.get("featured_image")
            ),

            status=status,

            featured=parse_bool(
                data.get("featured"),
                False
            ),

            published=published,

            publish_date=publish_date

        )

        db.session.add(
            book
        )

        db.session.flush()

        # ----------------------------------------------------
        # CATEGORIES
        # ----------------------------------------------------

        update_book_categories(
            book,
            category_ids
        )

        # ----------------------------------------------------
        # SEO
        # ----------------------------------------------------

        save_book_seo(
            book,
            data.get(
                "seo",
                {}
            )
            if isinstance(
                data.get("seo"),
                dict
            )
            else {}
        )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Book created successfully.",

            "book":
                book_to_dict(book)

        }), 201

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
                "Unable to create book.",

            "error":
                str(error)

        }), 500


# ============================================================
# UPDATE BOOK
# ============================================================

@admin_books_bp.route(
    "/<int:book_id>",
    methods=["PUT", "PATCH"]
)
def update_book(book_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(
        silent=True
    ) or {}

    try:

        book = Book.query.get(
            book_id
        )

        if not book:

            return jsonify({

                "success":
                    False,

                "message":
                    "Book not found."

            }), 404

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        if "title" in data:

            title = clean_string(
                data.get("title")
            )

            if not title:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Book title cannot be empty."

                }), 400

            book.title = title

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
                        "Book slug cannot be empty."

                }), 400

            existing = (
                Book.query
                .filter(
                    Book.slug == slug,
                    Book.id != book.id
                )
                .first()
            )

            if existing:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Book slug already exists."

                }), 409

            book.slug = slug

        # ----------------------------------------------------
        # TEXT FIELDS
        # ----------------------------------------------------

        fields = [

            "subtitle",
            "description",
            "short_description",
            "language",
            "tags",
            "cover_image",
            "banner_image",
            "featured_image"
        ]

        for field in fields:

            if field in data:

                setattr(
                    book,
                    field,
                    clean_string(
                        data.get(field)
                    )
                )

        # ----------------------------------------------------
        # AUTHOR
        # ----------------------------------------------------

        if "author_id" in data:

            author_id = data.get(
                "author_id"
            )

            validate_author(
                author_id
            )

            book.author_id = (
                parse_int(author_id)
                if author_id is not None
                else None
            )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        if "status" in data:

            status = clean_string(
                data.get("status")
            )

            allowed_statuses = (
                "draft",
                "published",
                "private"
            )

            if status not in allowed_statuses:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Invalid book status."

                }), 400

            book.status = status

            if status == "published":
                book.published = True

            elif status == "draft":
                book.published = False

            elif status == "private":
                book.published = False

        # ----------------------------------------------------
        # PUBLISHED
        # ----------------------------------------------------

        if "published" in data:

            book.published = parse_bool(
                data.get("published"),
                book.published
            )

            if book.published:
                book.status = "published"

        # ----------------------------------------------------
        # FEATURED
        # ----------------------------------------------------

        if "featured" in data:

            book.featured = parse_bool(
                data.get("featured"),
                book.featured
            )

        # ----------------------------------------------------
        # PUBLISH DATE
        # ----------------------------------------------------

        if "publish_date" in data:

            book.publish_date = parse_datetime(
                data.get("publish_date")
            )

        # ----------------------------------------------------
        # CATEGORIES
        # ----------------------------------------------------

        if "category_ids" in data:

            update_book_categories(
                book,
                data.get(
                    "category_ids"
                )
            )

        # ----------------------------------------------------
        # SEO
        # ----------------------------------------------------

        seo_data = data.get(
            "seo"
        )

        if isinstance(
            seo_data,
            dict
        ):

            save_book_seo(
                book,
                seo_data
            )

        # ----------------------------------------------------
        # COMMIT
        # ----------------------------------------------------

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Book updated successfully.",

            "book":
                book_to_dict(book)

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
                "Unable to update book.",

            "error":
                str(error)

        }), 500


# ============================================================
# DELETE BOOK
# ============================================================

@admin_books_bp.route(
    "/<int:book_id>",
    methods=["DELETE"]
)
def delete_book(book_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        book = Book.query.get(
            book_id
        )

        if not book:

            return jsonify({

                "success":
                    False,

                "message":
                    "Book not found."

            }), 404

        # ----------------------------------------------------
        # DELETE SEO
        # ----------------------------------------------------

        SEO.query.filter_by(
            entity_type="book",
            entity_id=book.id
        ).delete(
            synchronize_session=False
        )

        # ----------------------------------------------------
        # DELETE CATEGORY RELATIONS
        # ----------------------------------------------------

        BookCategory.query.filter_by(
            book_id=book.id
        ).delete(
            synchronize_session=False
        )

        # ----------------------------------------------------
        # DELETE BOOK
        # ----------------------------------------------------

        db.session.delete(
            book
        )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Book deleted successfully.",

            "book_id":
                book_id

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to delete book.",

            "error":
                str(error)

        }), 500


# ============================================================
# PUBLISH BOOK
# ============================================================

@admin_books_bp.route(
    "/<int:book_id>/publish",
    methods=["POST"]
)
def publish_book(book_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        book = Book.query.get(
            book_id
        )

        if not book:

            return jsonify({

                "success":
                    False,

                "message":
                    "Book not found."

            }), 404

        book.published = True
        book.status = "published"

        if not book.publish_date:

            book.publish_date = datetime.utcnow()

        save_book_seo(
            book,
            {}
        )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Book published successfully.",

            "book":
                book_to_dict(book)

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to publish book.",

            "error":
                str(error)

        }), 500


# ============================================================
# UNPUBLISH BOOK
# ============================================================

@admin_books_bp.route(
    "/<int:book_id>/unpublish",
    methods=["POST"]
)
def unpublish_book(book_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        book = Book.query.get(
            book_id
        )

        if not book:

            return jsonify({

                "success":
                    False,

                "message":
                    "Book not found."

            }), 404

        book.published = False
        book.status = "draft"

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Book moved to draft.",

            "book":
                book_to_dict(book)

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to unpublish book.",

            "error":
                str(error)

        }), 500


# ============================================================
# FEATURED BOOK TOGGLE
# ============================================================

@admin_books_bp.route(
    "/<int:book_id>/featured",
    methods=["POST"]
)
def toggle_featured(book_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(
        silent=True
    ) or {}

    try:

        book = Book.query.get(
            book_id
        )

        if not book:

            return jsonify({

                "success":
                    False,

                "message":
                    "Book not found."

            }), 404

        if "featured" in data:

            book.featured = parse_bool(
                data.get("featured")
            )

        else:

            book.featured = not bool(
                book.featured
            )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Featured status updated.",

            "featured":
                bool(book.featured),

            "book":
                book_to_dict(book)

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to update featured status.",

            "error":
                str(error)

        }), 500
