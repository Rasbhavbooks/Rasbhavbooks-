# =========================================================
# RASBHAV BOOKS
# PUBLIC BOOK API ROUTES
# Flask + SQLite
# =========================================================

from flask import Blueprint, jsonify, request

from app.models.book import Book
from app.models.category import Category
from app.models.book_category import BookCategory
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
# CATEGORY SERIALIZER
# =========================================================

def category_to_dict(category):
    return {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "description": category.description,
        "image": category.image,
        "parent_id": category.parent_id
    }


# =========================================================
# SEO SERIALIZER
# =========================================================

def seo_to_dict(seo):

    if not seo:
        return None

    return {
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

        "schema_data": seo.schema_data,

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


# =========================================================
# BOOK SERIALIZER
# =========================================================

def book_to_dict(book, include_categories=False, include_seo=False):

    data = {
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

    # -----------------------------------------------------
    # CATEGORIES
    # -----------------------------------------------------

    if include_categories:

        category_rows = (
            Category.query
            .join(
                BookCategory,
                BookCategory.category_id == Category.id
            )
            .filter(
                BookCategory.book_id == book.id
            )
            .order_by(
                Category.name.asc()
            )
            .all()
        )

        data["categories"] = [
            category_to_dict(category)
            for category in category_rows
        ]

    # -----------------------------------------------------
    # SEO
    # -----------------------------------------------------

    if include_seo:

        seo = SEO.query.filter_by(
            entity_type="book",
            entity_id=book.id
        ).first()

        data["seo"] = seo_to_dict(seo)

    return data


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

        search_pattern = f"%{search}%"

        query = query.filter(
            Book.title.ilike(search_pattern)
            |
            Book.description.ilike(search_pattern)
            |
            Book.short_description.ilike(search_pattern)
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

    if featured in (
        "1",
        "true",
        "yes"
    ):

        query = query.filter(
            Book.featured.is_(True)
        )

    # -----------------------------------------------------
    # ORDER
    # -----------------------------------------------------

    books = query.order_by(
        Book.created_at.desc()
    ).all()

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

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

    books = (
        Book.query
        .filter(
            Book.published.is_(True),
            Book.featured.is_(True)
        )
        .order_by(
            Book.created_at.desc()
        )
        .all()
    )

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

    return jsonify({
        "success": True,

        "book": book_to_dict(
            book,
            include_categories=True,
            include_seo=True
        )
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

    return jsonify({
        "success": True,

        "book": book_to_dict(
            book,
            include_categories=True,
            include_seo=True
        )
    })
