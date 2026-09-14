# =========================================================
# RASBHAV BOOKS
# PUBLIC AUTHOR ROUTES
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
# BOOK SERIALIZER
# =========================================================

def author_book_to_dict(book):

    return {
        "id": book.id,
        "title": book.title,
        "slug": book.slug,
        "subtitle": book.subtitle,
        "short_description": book.short_description,
        "language": book.language,
        "cover_image": book.cover_image,
        "featured_image": book.featured_image,
        "featured": bool(book.featured),
        "published": bool(book.published),
        "publish_date": (
            book.publish_date.isoformat()
            if book.publish_date
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
    # SEARCH AUTHOR
    # -----------------------------------------------------

    if search:

        query = query.filter(
            Author.name.ilike(f"%{search}%")
        )

    # -----------------------------------------------------
    # GET AUTHORS
    # -----------------------------------------------------

    authors = query.order_by(
        Author.name.asc()
    ).all()

    results = []

    for author in authors:

        results.append(
            author_to_dict(author)
        )

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
    # GET PUBLISHED BOOKS
    # -----------------------------------------------------

    books = Book.query.filter_by(
        author_id=author.id,
        published=True
    ).order_by(
        Book.created_at.desc()
    ).all()

    # -----------------------------------------------------
    # SEO
    # -----------------------------------------------------

    seo = SEO.query.filter_by(
        entity_type="author",
        entity_id=author.id
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

        "seo": seo_data
    })


# =========================================================
# GET AUTHOR BOOKS
# =========================================================

@author_bp.route("/<slug>/books", methods=["GET"])
def get_author_books(slug):

    author = Author.query.filter_by(
        slug=slug
    ).first_or_404()

    books = Book.query.filter_by(
        author_id=author.id,
        published=True
    ).order_by(
        Book.created_at.desc()
    ).all()

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
