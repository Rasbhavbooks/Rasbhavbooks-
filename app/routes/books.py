# =========================================================
# RASBHAV BOOKS
# PUBLIC BOOK ROUTES
# Flask + SQLite
# =========================================================

from flask import Blueprint, jsonify, request

from app.models.book import Book
from app.models.category import Category
from app.models.seo import SEO


# =========================================================
# BLUEPRINT
# =========================================================

books_bp = Blueprint(
    "books",
    __name__,
    url_prefix="/api/books"
)


# =========================================================
# BOOK SERIALIZER
# =========================================================

def book_to_dict(book):

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

        "featured": bool(book.featured),
        "published": bool(book.published),

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
        )
    }


# =========================================================
# GET ALL PUBLISHED BOOKS
# =========================================================

@books_bp.route("", methods=["GET"])
def get_books():

    query = Book.query.filter(
        Book.published.is_(True)
    )

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    search = request.args.get(
        "search",
        "",
        type=str
    ).strip()

    if search:

        query = query.filter(
            Book.title.ilike(f"%{search}%")
        )

    # -----------------------------------------------------
    # LANGUAGE FILTER
    # -----------------------------------------------------

    language = request.args.get(
        "language",
        "",
        type=str
    ).strip()

    if language:

        query = query.filter(
            Book.language == language
        )

    # -----------------------------------------------------
    # FEATURED FILTER
    # -----------------------------------------------------

    featured = request.args.get(
        "featured",
        "",
        type=str
    ).strip().lower()

    if featured in ("1", "true", "yes"):

        query = query.filter(
            Book.featured.is_(True)
        )

    # -----------------------------------------------------
    # ORDER
    # -----------------------------------------------------

    books = query.order_by(
        Book.created_at.desc()
    ).all()

    return jsonify({
        "success": True,
        "count": len(books),
        "books": [
            book_to_dict(book)
            for book in books
        ]
    })


# =========================================================
# GET FEATURED BOOKS
# =========================================================

@books_bp.route("/featured", methods=["GET"])
def get_featured_books():

    books = Book.query.filter(
        Book.published.is_(True),
        Book.featured.is_(True)
    ).order_by(
        Book.created_at.desc()
    ).all()

    return jsonify({
        "success": True,
        "count": len(books),
        "books": [
            book_to_dict(book)
            for book in books
        ]
    })


# =========================================================
# GET SINGLE PUBLISHED BOOK
# =========================================================

@books_bp.route("/<slug>", methods=["GET"])
def get_book(slug):

    book = Book.query.filter_by(
        slug=slug,
        published=True
    ).first_or_404()

    # -----------------------------------------------------
    # SEO
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # CATEGORIES
    # -----------------------------------------------------

    categories = []

    try:

        categories = [
            {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
                "description": category.description,
                "image": category.image,
                "parent_id": category.parent_id
            }
            for category in book.categories
        ]

    except Exception:

        categories = []

    # -----------------------------------------------------
    # FINAL RESPONSE
    # -----------------------------------------------------

    response = book_to_dict(book)

    response["categories"] = categories

    response["seo"] = seo_data

    return jsonify({
        "success": True,
        "book": response
    })


# =========================================================
# GET BOOK BY ID
# =========================================================

@books_bp.route("/id/<int:book_id>", methods=["GET"])
def get_book_by_id(book_id):

    book = Book.query.filter_by(
        id=book_id,
        published=True
    ).first_or_404()

    response = book_to_dict(book)

    # -----------------------------------------------------
    # CATEGORIES
    # -----------------------------------------------------

    try:

        response["categories"] = [
            {
                "id": category.id,
                "name": category.name,
                "slug": category.slug
            }
            for category in book.categories
        ]

    except Exception:

        response["categories"] = []

    # -----------------------------------------------------
    # SEO
    # -----------------------------------------------------

    seo = SEO.query.filter_by(
        entity_type="book",
        entity_id=book.id
    ).first()

    if seo:

        response["seo"] = {
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

    else:

        response["seo"] = None

    return jsonify({
        "success": True,
        "book": response
    })
