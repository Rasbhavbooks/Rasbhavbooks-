# =========================================================
# RASBHAV BOOKS
# PUBLIC SEARCH API
# Flask + SQLite
# =========================================================

from flask import Blueprint, request, jsonify

from app.models.book import Book
from app.models.author import Author


# =========================================================
# BLUEPRINT
# =========================================================

search_bp = Blueprint(
    "search",
    __name__,
    url_prefix="/search"
)


# =========================================================
# BOOK SERIALIZER
# =========================================================

def search_book_to_dict(book):

    author = None

    if book.author_id:
        author = Author.query.filter_by(
            id=book.author_id
        ).first()

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

        "author": (
            {
                "id": author.id,
                "name": author.name,
                "slug": author.slug
            }
            if author
            else None
        ),

        "publish_date": (
            book.publish_date.isoformat()
            if book.publish_date
            else None
        )
    }


# =========================================================
# SEARCH BOOKS
# =========================================================

@search_bp.route("", methods=["GET"])
@search_bp.route("/", methods=["GET"])
def search_books():

    query_text = request.args.get(
        "q",
        "",
        type=str
    ).strip()

    # -----------------------------------------------------
    # EMPTY SEARCH
    # -----------------------------------------------------

    if not query_text:

        return jsonify({
            "success": True,
            "query": "",
            "count": 0,
            "results": []
        })


    # -----------------------------------------------------
    # SEARCH PATTERN
    # -----------------------------------------------------

    search_pattern = f"%{query_text}%"


    # -----------------------------------------------------
    # PUBLIC BOOK QUERY
    # -----------------------------------------------------

    query = (
        Book.query
        .outerjoin(
            Author,
            Author.id == Book.author_id
        )
        .filter(
            Book.published.is_(True)
        )
        .filter(
            (
                Book.title.ilike(search_pattern)
            )
            |
            (
                Book.subtitle.ilike(search_pattern)
            )
            |
            (
                Book.description.ilike(search_pattern)
            )
            |
            (
                Book.short_description.ilike(search_pattern)
            )
            |
            (
                Book.language.ilike(search_pattern)
            )
            |
            (
                Book.tags.ilike(search_pattern)
            )
            |
            (
                Author.name.ilike(search_pattern)
            )
        )
        .order_by(
            Book.created_at.desc()
        )
    )


    # -----------------------------------------------------
    # LIMIT
    # -----------------------------------------------------

    limit = request.args.get(
        "limit",
        50,
        type=int
    )

    if limit < 1:
        limit = 1

    if limit > 100:
        limit = 100


    books = query.limit(limit).all()


    # -----------------------------------------------------
    # RESULTS
    # -----------------------------------------------------

    results = [
        search_book_to_dict(book)
        for book in books
    ]


    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return jsonify({

        "success": True,

        "query": query_text,

        "count": len(results),

        "results": results
    })
