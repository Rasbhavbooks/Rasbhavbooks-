from flask import Blueprint, jsonify
from app.models.book import Book

books_bp = Blueprint(
    "books",
    __name__,
    url_prefix="/api/books"
)


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


@books_bp.route("/<slug>", methods=["GET"])
def get_book(slug):
    book = Book.query.filter_by(
        slug=slug,
        published=True
    ).first_or_404()

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
        "publish_date": book.publish_date.isoformat()
        if book.publish_date else None
    })
