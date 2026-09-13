from flask import Blueprint, request, jsonify, session
from datetime import datetime
import json

from app import db
from app.models.book import Book
from app.models.seo import SEO


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
# SEO DEFAULTS
# =========================================================

def create_default_seo(book):

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

    seo = SEO(
        entity_type="book",
        entity_id=book.id,

        meta_title=f"{book.title} | Rasbhav Books",

        meta_description=description,

        focus_keyword=book.title,

        canonical_url=f"/books/{book.slug}",

        robots="index, follow",

        og_title=f"{book.title} | Rasbhav Books",

        og_description=description,

        og_image=book.cover_image,

        schema_data=json.dumps(
            schema,
            ensure_ascii=False
        )
    )

    db.session.add(seo)

    return seo


# =========================================================
# UPDATE BOOK SEO
# =========================================================

def save_book_seo(book, data):

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


    # -----------------------------------------------------
    # META TITLE
    # -----------------------------------------------------

    seo.meta_title = (
        str(
            data.get(
                "meta_title",
                seo.meta_title
                or f"{book.title} | Rasbhav Books"
            )
        ).strip()
    )


    # -----------------------------------------------------
    # META DESCRIPTION
    # -----------------------------------------------------

    seo.meta_description = (
        str(
            data.get(
                "meta_description",
                seo.meta_description
                or description
            )
        ).strip()
    )


    # -----------------------------------------------------
    # FOCUS KEYWORD
    # -----------------------------------------------------

    seo.focus_keyword = (
        str(
            data.get(
                "focus_keyword",
                seo.focus_keyword
                or book.title
            )
        ).strip()
    )


    # -----------------------------------------------------
    # CANONICAL
    # -----------------------------------------------------

    seo.canonical_url = (
        str(
            data.get(
                "canonical_url",
                seo.canonical_url
                or f"/books/{book.slug}"
            )
        ).strip()
    )


    # -----------------------------------------------------
    # ROBOTS
    # -----------------------------------------------------

    seo.robots = (
        str(
            data.get(
                "robots",
                seo.robots
                or "index, follow"
            )
        ).strip()
    )


    # -----------------------------------------------------
    # OG TITLE
    # -----------------------------------------------------

    seo.og_title = (
        str(
            data.get(
                "og_title",
                seo.og_title
                or seo.meta_title
            )
        ).strip()
    )


    # -----------------------------------------------------
    # OG DESCRIPTION
    # -----------------------------------------------------

    seo.og_description = (
        str(
            data.get(
                "og_description",
                seo.og_description
                or seo.meta_description
            )
        ).strip()
    )


    # -----------------------------------------------------
    # OG IMAGE
    # -----------------------------------------------------

    seo.og_image = (
        str(
            data.get(
                "og_image",
                seo.og_image
                or book.cover_image
                or ""
            )
        ).strip()
    )


    # -----------------------------------------------------
    # SCHEMA
    # -----------------------------------------------------

    schema_data = data.get(
        "schema_data"
    )


    if schema_data:

        if isinstance(
            schema_data,
            str
        ):

            seo.schema_data = schema_data

        else:

            seo.schema_data = json.dumps(
                schema_data,
                ensure_ascii=False
            )

    elif not seo.schema_data:

        schema = {
            "@context": "https://schema.org",
            "@type": "Book",
            "name": book.title,
            "url": f"/books/{book.slug}",
            "description": seo.meta_description
        }

        if book.cover_image:
            schema["image"] = book.cover_image

        seo.schema_data = json.dumps(
            schema,
            ensure_ascii=False
        )


    return seo


# =========================================================
# BOOK SERIALIZER
# =========================================================

def book_data(book):

    seo = SEO.query.filter_by(
        entity_type="book",
        entity_id=book.id
    ).first()


    seo_data = None

    if seo:

        seo_data = {
            "id": seo.id,
            "entity_type": seo.entity_type,
            "entity_id": seo.entity_id,
            "meta_title": seo.meta_title,
            "meta_description": seo.meta_description,
            "focus_keyword": seo.focus_keyword,
            "canonical_url": seo.canonical_url,
            "robots": seo.robots,
            "og_title": seo.og_title,
            "og_description": seo.og_description,
            "og_image": seo.og_image,
            "schema_data": seo.schema_data
        }


    return {

        "id": book.id,

        "title": book.title,

        "slug": book.slug,

        "subtitle": book.subtitle,

        "description": book.description,

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
            book.featured,

        "published":
            book.published,

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

        "seo": seo_data
    }


# =========================================================
# GET ALL BOOKS
# =========================================================

@admin_books_bp.route(
    "",
    methods=["GET"]
)
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

@admin_books_bp.route(
    "/<int:book_id>",
    methods=["GET"]
)
def get_book(book_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error


    book = Book.query.get_or_404(
        book_id
    )


    return jsonify({

        "success": True,

        "book": book_data(book)

    })


# =========================================================
# CREATE BOOK
# =========================================================

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


    title = str(
        data.get(
            "title",
            ""
        )
    ).strip()


    slug = str(
        data.get(
            "slug",
            ""
        )
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
                str(
                    data["publish_date"]
                )
            )

        except ValueError:

            return jsonify({
                "success": False,
                "message": "Invalid publish_date format."
            }), 400


    # =====================================================
    # CREATE BOOK
    # =====================================================

    book = Book(

        title=title,

        slug=slug,

        subtitle=data.get(
            "subtitle"
        ),

        description=data.get(
            "description"
        ),

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

    db.session.flush()


    # =====================================================
    # CREATE DEFAULT SEO
    # =====================================================

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
                "message":
                    "Book title cannot be empty."
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
                        str(
                            publish_date
                        )
                    )
                )

            except ValueError:

                return jsonify({
                    "success": False,
                    "message":
                        "Invalid publish_date format."
                }), 400

        else:

            book.publish_date = None


    # =====================================================
    # UPDATE SEO
    # =====================================================

    save_book_seo(
        book,
        data
    )


    # =====================================================
    # SAVE
    # =====================================================

    db.session.commit()


    return jsonify({

        "success": True,

        "message":
            "Book updated successfully.",

        "book":
            book_data(book)

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


    # =====================================================
    # DELETE BOOK SEO
    # =====================================================

    SEO.query.filter_by(
        entity_type="book",
        entity_id=book.id
    ).delete(
        synchronize_session=False
    )


    db.session.delete(
        book
    )


    db.session.commit()


    return jsonify({

        "success": True,

        "message":
            "Book deleted successfully."

    })
