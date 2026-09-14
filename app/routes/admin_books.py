# ============================================================
# RASBHAV BOOKS
# ADMIN BOOK ROUTES / API
#
# File:
# app/routes/admin_books.py
#
# Architecture:
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
# - Publish date validation
# - SEO CRUD
# - JSON-LD Book Schema
# - Safe JSON responses
# - Database rollback on errors
# ============================================================


from flask import Blueprint, request, jsonify, session
from datetime import datetime
import json

from app import db
from app.models.book import Book
from app.models.seo import SEO


# ============================================================
# BLUEPRINT
# ============================================================

admin_books_bp = Blueprint(
    "admin_books",
    __name__,
    url_prefix="/api/admin/books"
)


# ============================================================
# ADMIN AUTHENTICATION
# ============================================================

def admin_required():
    """
    Check whether an admin is logged in.
    """

    if not session.get("admin_id"):
        return jsonify({
            "success": False,
            "message": "Admin login required."
        }), 401

    return None


# ============================================================
# HELPERS
# ============================================================

def clean_string(value, default=None):
    """
    Convert a value into a clean string.

    Empty strings become default.
    """

    if value is None:
        return default

    value = str(value).strip()

    if not value:
        return default

    return value


def parse_bool(value, default=False):
    """
    Safely convert common values into boolean.
    """

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
            "on"
        ):
            return True

        if value in (
            "false",
            "0",
            "no",
            "off"
        ):
            return False

    return default


def parse_datetime(value):
    """
    Convert ISO datetime string into datetime object.
    """

    if not value:
        return None

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
# SEO SCHEMA
# ============================================================

def build_book_schema(book):
    """
    Build Schema.org Book JSON-LD.
    """

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

    return schema


# ============================================================
# CREATE DEFAULT SEO
# ============================================================

def create_default_seo(book):
    """
    Create SEO record for a new book.
    """

    description = (
        book.short_description
        or book.description
        or f"Read {book.title} online on Rasbhav Books."
    )

    schema = build_book_schema(book)

    seo = SEO(
        entity_type="book",

        entity_id=book.id,

        meta_title=(
            f"{book.title} | Rasbhav Books"
        ),

        meta_description=description,

        focus_keyword=book.title,

        canonical_url=(
            f"/books/{book.slug}"
        ),

        robots="index, follow",

        og_title=(
            f"{book.title} | Rasbhav Books"
        ),

        og_description=description,

        og_image=book.cover_image,

        schema_data=json.dumps(
            schema,
            ensure_ascii=False
        )
    )

    db.session.add(seo)

    return seo


# ============================================================
# SAVE / UPDATE BOOK SEO
# ============================================================

def save_book_seo(book, data):
    """
    Create or update SEO information for a book.
    """

    seo = SEO.query.filter_by(
        entity_type="book",
        entity_id=book.id
    ).first()

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

    # --------------------------------------------------------
    # META TITLE
    # --------------------------------------------------------

    meta_title = data.get(
        "meta_title"
    )

    if meta_title is not None:

        seo.meta_title = clean_string(
            meta_title,
            f"{book.title} | Rasbhav Books"
        )

    elif not seo.meta_title:

        seo.meta_title = (
            f"{book.title} | Rasbhav Books"
        )

    # --------------------------------------------------------
    # META DESCRIPTION
    # --------------------------------------------------------

    meta_description = data.get(
        "meta_description"
    )

    if meta_description is not None:

        seo.meta_description = clean_string(
            meta_description,
            description
        )

    elif not seo.meta_description:

        seo.meta_description = description

    # --------------------------------------------------------
    # FOCUS KEYWORD
    # --------------------------------------------------------

    focus_keyword = data.get(
        "focus_keyword"
    )

    if focus_keyword is not None:

        seo.focus_keyword = clean_string(
            focus_keyword,
            book.title
        )

    elif not seo.focus_keyword:

        seo.focus_keyword = book.title

    # --------------------------------------------------------
    # CANONICAL URL
    # --------------------------------------------------------

    canonical_url = data.get(
        "canonical_url"
    )

    if canonical_url is not None:

        seo.canonical_url = clean_string(
            canonical_url,
            f"/books/{book.slug}"
        )

    elif not seo.canonical_url:

        seo.canonical_url = (
            f"/books/{book.slug}"
        )

    # --------------------------------------------------------
    # ROBOTS
    # --------------------------------------------------------

    robots = data.get(
        "robots"
    )

    if robots is not None:

        seo.robots = clean_string(
            robots,
            "index, follow"
        )

    elif not seo.robots:

        seo.robots = "index, follow"

    # --------------------------------------------------------
    # OPEN GRAPH TITLE
    # --------------------------------------------------------

    og_title = data.get(
        "og_title"
    )

    if og_title is not None:

        seo.og_title = clean_string(
            og_title,
            seo.meta_title
        )

    elif not seo.og_title:

        seo.og_title = seo.meta_title

    # --------------------------------------------------------
    # OPEN GRAPH DESCRIPTION
    # --------------------------------------------------------

    og_description = data.get(
        "og_description"
    )

    if og_description is not None:

        seo.og_description = clean_string(
            og_description,
            seo.meta_description
        )

    elif not seo.og_description:

        seo.og_description = (
            seo.meta_description
        )

    # --------------------------------------------------------
    # OPEN GRAPH IMAGE
    # --------------------------------------------------------

    og_image = data.get(
        "og_image"
    )

    if og_image is not None:

        seo.og_image = clean_string(
            og_image,
            book.cover_image
        )

    elif not seo.og_image:

        seo.og_image = book.cover_image

    # --------------------------------------------------------
    # SCHEMA DATA
    # --------------------------------------------------------

    schema_data = data.get(
        "schema_data"
    )

    if schema_data:

        if isinstance(
            schema_data,
            str
        ):

            # Validate JSON before saving.
            try:

                json.loads(
                    schema_data
                )

            except json.JSONDecodeError:

                raise ValueError(
                    "Invalid schema_data JSON."
                )

            seo.schema_data = schema_data

        else:

            seo.schema_data = json.dumps(
                schema_data,
                ensure_ascii=False
            )

    else:

        schema = build_book_schema(
            book
        )

        seo.schema_data = json.dumps(
            schema,
            ensure_ascii=False
        )

    return seo


# ============================================================
# BOOK SERIALIZER
# ============================================================

def book_data(book):
    """
    Convert Book database object into API JSON.
    """

    seo = SEO.query.filter_by(
        entity_type="book",
        entity_id=book.id
    ).first()

    seo_data = None

    if seo:

        seo_data = {

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
                seo.schema_data
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

        "created_at": (

            book.created_at.isoformat()

            if book.created_at

            else None
        ),

        "updated_at": (

            book.updated_at.isoformat()

            if book.updated_at

            else None
        ),

        "seo":
            seo_data
    }


# ============================================================
# GET ALL BOOKS
# ============================================================

@admin_books_bp.route(
    "",
    methods=["GET"]
)
def get_books():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        books = Book.query.order_by(
            Book.created_at.desc()
        ).all()

        return jsonify({

            "success": True,

            "count": len(books),

            "books": [
                book_data(book)
                for book in books
            ]

        })

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success": False,

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

                "success": False,

                "message":
                    "Book not found."

            }), 404

        return jsonify({

            "success": True,

            "book":
                book_data(book)

        })

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success": False,

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
def create_book():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(
        silent=True
    ) or {}

    title = clean_string(
        data.get("title")
    )

    slug = clean_string(
        data.get("slug")
    )

    # --------------------------------------------------------
    # REQUIRED TITLE
    # --------------------------------------------------------

    if not title:

        return jsonify({

            "success": False,

            "message":
                "Book title is required."

        }), 400

    # --------------------------------------------------------
    # REQUIRED SLUG
    # --------------------------------------------------------

    if not slug:

        return jsonify({

            "success": False,

            "message":
                "Book slug is required."

        }), 400

    # --------------------------------------------------------
    # SLUG CHECK
    # --------------------------------------------------------

    existing_book = Book.query.filter_by(
        slug=slug
    ).first()

    if existing_book:

        return jsonify({

            "success": False,

            "message":
                "Book slug already exists."

        }), 409

    # --------------------------------------------------------
    # PUBLISH DATE
    # --------------------------------------------------------

    try:

        publish_date = parse_datetime(
            data.get("publish_date")
        )

    except ValueError as error:

        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 400

    # --------------------------------------------------------
    # CREATE BOOK
    # --------------------------------------------------------

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

        author_id=data.get(
            "author_id"
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

        status=clean_string(
            data.get("status"),
            "draft"
        ),

        featured=parse_bool(
            data.get("featured"),
            False
        ),

        published=parse_bool(
            data.get("published"),
            False
        ),

        publish_date=publish_date

    )

    try:

        db.session.add(
            book
        )

        db.session.flush()

        # ----------------------------------------------------
        # SEO
        # ----------------------------------------------------

        save_book_seo(
            book,
            data
        )

        db.session.commit()

        return jsonify({

            "success": True,

            "message":
                "Book created successfully.",

            "book":
                book_data(book)

        }), 201

    except ValueError as error:

        db.session.rollback()

        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 400

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success": False,

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
    methods=["PUT"]
)
def update_book(book_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    book = Book.query.get(
        book_id
    )

    if not book:

        return jsonify({

            "success": False,

            "message":
                "Book not found."

        }), 404

    data = request.get_json(
        silent=True
    ) or {}

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    if "title" in data:

        title = clean_string(
            data.get("title")
        )

        if not title:

            return jsonify({

                "success": False,

                "message":
                    "Book title cannot be empty."

            }), 400

        book.title = title

    # --------------------------------------------------------
    # SLUG
    # --------------------------------------------------------

    if "slug" in data:

        slug = clean_string(
            data.get("slug")
        )

        if not slug:

            return jsonify({

                "success": False,

                "message":
                    "Book slug cannot be empty."

            }), 400

        existing = Book.query.filter(
            Book.slug == slug,
            Book.id != book.id
        ).first()

        if existing:

            return jsonify({

                "success": False,

                "message":
                    "Book slug already exists."

            }), 409

        book.slug = slug

    # --------------------------------------------------------
    # NORMAL FIELDS
    # --------------------------------------------------------

    fields = [

        "subtitle",

        "description",

        "short_description",

        "author_id",

        "language",

        "tags",

        "cover_image",

        "banner_image",

        "featured_image",

        "status"

    ]

    for field in fields:

        if field in data:

            value = data[field]

            if isinstance(
                value,
                str
            ):

                value = (
                    value.strip()
                    or None
                )

            setattr(
                book,
                field,
                value
            )

    # --------------------------------------------------------
    # FEATURED
    # --------------------------------------------------------

    if "featured" in data:

        book.featured = parse_bool(
            data.get("featured")
        )

    # --------------------------------------------------------
    # PUBLISHED
    # --------------------------------------------------------

    if "published" in data:

        book.published = parse_bool(
            data.get("published")
        )

    # --------------------------------------------------------
    # PUBLISH DATE
    # --------------------------------------------------------

    if "publish_date" in data:

        try:

            book.publish_date = (
                parse_datetime(
                    data.get(
                        "publish_date"
                    )
                )
            )

        except ValueError as error:

            return jsonify({

                "success": False,

                "message":
                    str(error)

            }), 400

    # --------------------------------------------------------
    # UPDATE SEO
    # --------------------------------------------------------

    try:

        save_book_seo(
            book,
            data
        )

        db.session.commit()

        return jsonify({

            "success": True,

            "message":
                "Book updated successfully.",

            "book":
                book_data(book)

        })

    except ValueError as error:

        db.session.rollback()

        return jsonify({

            "success": False,

            "message":
                str(error)

        }), 400

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success": False,

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

    book = Book.query.get(
        book_id
    )

    if not book:

        return jsonify({

            "success": False,

            "message":
                "Book not found."

        }), 404

    try:

        # ----------------------------------------------------
        # DELETE BOOK SEO
        # ----------------------------------------------------

        SEO.query.filter_by(

            entity_type="book",

            entity_id=book.id

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

            "success": True,

            "message":
                "Book deleted successfully."

        })

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success": False,

            "message":
                "Unable to delete book.",

            "error":
                str(error)

        }), 500


# ============================================================
# END OF ADMIN BOOK ROUTES
# ============================================================
