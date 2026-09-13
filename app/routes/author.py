from flask import Blueprint, jsonify

from app.models.author import Author
from app.models.book import Book


author_bp = Blueprint(
    "author",
    __name__,
    url_prefix="/api/authors"
)


# =========================================================
# GET ALL AUTHORS
# =========================================================

@author_bp.route("", methods=["GET"])
def get_authors():

    authors = Author.query.order_by(
        Author.name.asc()
    ).all()

    results = []

    for author in authors:

        results.append({
            "id": author.id,
            "name": author.name,
            "slug": author.slug,
            "biography": author.biography,
            "profile_image": author.profile_image
        })

    return jsonify(results)


# =========================================================
# GET SINGLE AUTHOR
# =========================================================

@author_bp.route("/<slug>", methods=["GET"])
def get_author(slug):

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
        "id": author.id,
        "name": author.name,
        "slug": author.slug,
        "biography": author.biography,
        "profile_image": author.profile_image,

        "books": [
            {
                "id": book.id,
                "title": book.title,
                "slug": book.slug,
                "subtitle": book.subtitle,
                "language": book.language,
                "cover_image": book.cover_image,
                "featured": book.featured
            }
            for book in books
        ]
    })
