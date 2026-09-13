from flask import Blueprint, jsonify

from app.models.book import Book
from app.models.seo import SEO


books_bp = Blueprint(
    "books",
    __name__,
    url_prefix="/api/books"
)


# =========================================================
# GET ALL PUBLISHED BOOKS
# =========================================================

@books_bp.route("", methods=["GET"])
def get_books():

    books = Book.query.filter_by(
        published=True
    ).order_by(
        Book.created_at.desc()
    ).all()

    return jsonify([
        {
            "id": book.id,
            "title": book.title,
            "slug": book.slug,
            "subtitle": book.subtitle,
            "short_description": book.short_description,
            "language": book.language,
            "cover_image": book.cover_image,
            "featured": book.featured,
            "published": book.published
        }
        for book in books
    ])


# =========================================================
# GET SINGLE PUBLISHED BOOK
# WITH SEO
# =========================================================

@books_bp.route("/<slug>", methods=["GET"])
def get_book(slug):

    book = Book.query.filter_by(
        slug=slug,
        published=True
    ).first_or_404()


    # -----------------------------------------------------
    # GET BOOK SEO
    # -----------------------------------------------------

    seo = SEO.query.filter_by(
        entity_type="book",
        entity_id=book.id
    ).first()


    # -----------------------------------------------------
    # SEO DATA
    # -----------------------------------------------------

    seo_data = None

    if seo:

        seo_data = {
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
    # BOOK RESPONSE
    # -----------------------------------------------------

    return jsonify({

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
            if book.publish_date
            else None
        ),

        # -------------------------------------------------
        # SEO
        # -------------------------------------------------

        "seo": seo_data

    })
