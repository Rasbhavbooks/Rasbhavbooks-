from flask import Blueprint, request, jsonify, session
from datetime import datetime

from app import db
from app.models.book import Book


admin_books_bp = Blueprint(
    "admin_books",
    __name__,
    url_prefix="/api/admin/books"
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
# BOOK SERIALIZER
# =========================================================

def book_data(book):

    return {
        "id": book.id,
        "title": book.title,
        "slug": book.slug,
        "subtitle": book.subtitle,
        "description": book.description,
        "short_description": book.short_description,
        "author_id": book.author_id,
        "language": book.language,
        "tags": book.tags,
        "cover_image": book.cover_image,
        "banner_image": book.banner_image,
        "featured_image": book.featured_image,
        "status": book.status,
        "featured": book.featured,
        "published": book.published,

        "publish_date": (
            book.publish_date.isoformat()
            if book.publish_date else None
        ),

        "created_at": (
            book.created_at.isoformat()
            if book.created_at else None
        ),

        "updated_at": (
            book.updated_at.isoformat()
            if book.updated_at else None
        )
    }


# =========================================================
# GET ALL BOOKS
# =========================================================

@admin_books_bp.route("", methods=["GET"])
def get_books():

    auth_error = admin_required()

    if auth_error:
        return auth_error

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


# =========================================================
# GET SINGLE BOOK
# =========================================================

@admin_books_bp.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    book = Book.query.get_or_404(book_id)

    return jsonify({
        "success": True,
        "book": book_data(book)
    })


# =========================================================
# CREATE BOOK
# =========================================================

@admin_books_bp.route("", methods=["POST"])
def create_book():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}

    title = str(
        data.get("title", "")
    ).strip()

    slug = str(
        data.get("slug", "")
    ).strip()

    if not title:

        return jsonify({
            "success": False,
            "message": "Book title is required."
        }), 400

    if not slug:

        return jsonify({
            "success": False,
            "message": "Book slug is required."
        }), 400

    existing_book = Book.query.filter_by(
        slug=slug
    ).first()

    if existing_book:

        return jsonify({
            "success": False,
            "message": "Book slug already exists."
        }), 409


    # =====================================================
    # PUBLISH DATE
    # =====================================================

    publish_date = None

    if data.get("publish_date"):

        try:

            publish_date = datetime.fromisoformat(
                str(data["publish_date"])
            )

        except ValueError:

            return jsonify({
                "success": False,
                "message": "Invalid publish_date format."
            }), 400


    # =====================================================
    # CREATE
    # =====================================================

    book = Book(

        title=title,

        slug=slug,

        subtitle=data.get("subtitle"),

        description=data.get("description"),

        short_description=data.get(
            "short_description"
        ),

        author_id=data.get(
            "author_id"
        ),

        language=data.get(
            "language"
        ),

        tags=data.get(
            "tags"
        ),

        cover_image=data.get(
            "cover_image"
        ),

        banner_image=data.get(
            "banner_image"
        ),

        featured_image=data.get(
            "featured_image"
        ),

        status=data.get(
            "status",
            "draft"
        ),

        featured=bool(
            data.get(
                "featured",
                False
            )
        ),

        published=bool(
            data.get(
                "published",
                False
            )
        ),

        publish_date=publish_date
    )


    db.session.add(book)

    db.session.commit()


    return jsonify({
        "success": True,
        "message": "Book created successfully.",
        "book": book_data(book)
    }), 201


# =========================================================
# UPDATE BOOK
# =========================================================

@admin_books_bp.route(
    "/<int:book_id>",
    methods=["PUT"]
)
def update_book(book_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    book = Book.query.get_or_404(
        book_id
    )

    data = request.get_json(
        silent=True
    ) or {}


    # =====================================================
    # TITLE
    # =====================================================

    if "title" in data:

        title = str(
            data["title"]
        ).strip()

        if not title:

            return jsonify({
                "success": False,
                "message": "Book title cannot be empty."
            }), 400

        book.title = title


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
                "message": "Book slug cannot be empty."
            }), 400

        existing = Book.query.filter(
            Book.slug == slug,
            Book.id != book.id
        ).first()

        if existing:

            return jsonify({
                "success": False,
                "message": "Book slug already exists."
            }), 409

        book.slug = slug


    # =====================================================
    # NORMAL FIELDS
    # =====================================================

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

            setattr(
                book,
                field,
                data[field]
            )


    # =====================================================
    # FEATURED
    # =====================================================

    if "featured" in data:

        book.featured = bool(
            data["featured"]
        )


    # =====================================================
    # PUBLISHED
    # =====================================================

    if "published" in data:

        book.published = bool(
            data["published"]
        )


    # =====================================================
    # PUBLISH DATE
    # =====================================================

    if "publish_date" in data:

        publish_date = data[
            "publish_date"
        ]

        if publish_date:

            try:

                book.publish_date = (
                    datetime.fromisoformat(
                        str(publish_date)
                    )
                )

            except ValueError:

                return jsonify({
                    "success": False,
                    "message": "Invalid publish_date format."
                }), 400

        else:

            book.publish_date = None


    # =====================================================
    # SAVE
    # =====================================================

    db.session.commit()


    return jsonify({
        "success": True,
        "message": "Book updated successfully.",
        "book": book_data(book)
    })


# =========================================================
# DELETE BOOK
# =========================================================

@admin_books_bp.route(
    "/<int:book_id>",
    methods=["DELETE"]
)
def delete_book(book_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    book = Book.query.get_or_404(
        book_id
    )

    db.session.delete(book)

    db.session.commit()


    return jsonify({
        "success": True,
        "message": "Book deleted successfully."
    })
