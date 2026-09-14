# =========================================================
# RASBHAV BOOKS
# PUBLIC AUTHOR API ROUTES
# Flask + SQLite
# =========================================================

from flask import Blueprint, jsonify, request

from app.models.author import Author
from app.models.book import Book
from app.models.seo import SEO


# =========================================================
# BLUEPRINT
# =========================================================

author_bp = Blueprint(
    "author",
    __name__,
    url_prefix="/api/authors"
)


# =========================================================
# AUTHOR SERIALIZER
# =========================================================

def author_to_dict(author):

    return {
        "id": author.id,
        "name": author.name,
        "slug": author.slug,
        "biography": author.biography,
        "profile_image": author.profile_image
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

def author_book_to_dict(book):

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
# GET ALL AUTHORS
# =========================================================

@author_bp.route("", methods=["GET"])
def get_authors():

    search = request.args.get(
        "search",
        "",
        type=str
    ).strip()

    query = Author.query

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    if search:

        query = query.filter(
            Author.name.ilike(
                f"%{search}%"
            )
        )

    # -----------------------------------------------------
    # AUTHORS
    # -----------------------------------------------------

    authors = query.order_by(
        Author.name.asc()
    ).all()

    results = [
        author_to_dict(author)
        for author in authors
    ]

    return jsonify({
        "success": True,
        "count": len(results),
        "authors": results
    })


# =========================================================
# GET SINGLE AUTHOR
# =========================================================

@author_bp.route("/<slug>", methods=["GET"])
def get_author(slug):

    author = Author.query.filter_by(
        slug=slug
    ).first_or_404()

    # -----------------------------------------------------
    # PUBLISHED BOOKS
    # -----------------------------------------------------

    books = (
        Book.query
        .filter(
            Book.author_id == author.id,
            Book.published.is_(True)
        )
        .order_by(
            Book.created_at.desc()
        )
        .all()
    )

    # -----------------------------------------------------
    # SEO
    # -----------------------------------------------------

    seo = SEO.query.filter_by(
        entity_type="author",
        entity_id=author.id
    ).first()

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return jsonify({

        "success": True,

        "author": author_to_dict(author),

        "books": [
            author_book_to_dict(book)
            for book in books
        ],

        "book_count": len(books),

        "seo": seo_to_dict(seo)
    })


# =========================================================
# GET AUTHOR BOOKS
# =========================================================

@author_bp.route("/<slug>/books", methods=["GET"])
def get_author_books(slug):

    author = Author.query.filter_by(
        slug=slug
    ).first_or_404()

    books = (
        Book.query
        .filter(
            Book.author_id == author.id,
            Book.published.is_(True)
        )
        .order_by(
            Book.created_at.desc()
        )
        .all()
    )

    return jsonify({

        "success": True,

        "author": {
            "id": author.id,
            "name": author.name,
            "slug": author.slug
        },

        "count": len(books),

        "books": [
            author_book_to_dict(book)
            for book in books
        ]
    })
