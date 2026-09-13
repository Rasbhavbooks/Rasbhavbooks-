from flask import Blueprint, request, jsonify
from app import db

from app.models.book import Book
from app.models.author import Author
from app.models.category import Category


search_bp = Blueprint(
    "search",
    __name__,
    url_prefix="/api/search"
)


@search_bp.route("", methods=["GET"])
def search_books():

    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({
            "success": True,
            "query": "",
            "count": 0,
            "results": []
        })


    search_term = f"%{query}%"


    books = Book.query.outerjoin(
        Author,
        Book.author_id == Author.id
    ).filter(
        Book.published.is_(True)
    ).filter(
        db.or_(
            Book.title.ilike(search_term),
            Book.subtitle.ilike(search_term),
            Book.description.ilike(search_term),
            Book.short_description.ilike(search_term),
            Book.tags.ilike(search_term),
            Author.name.ilike(search_term)
        )
    ).order_by(
        Book.title.asc()
    ).all()


    results = []


    for book in books:

        author_name = None

        if book.author_id:
            author = Author.query.get(book.author_id)

            if author:
                author_name = author.name


        results.append({
            "id": book.id,
            "title": book.title,
            "slug": book.slug,
            "subtitle": book.subtitle,
            "short_description": book.short_description,
            "language": book.language,
            "tags": book.tags,
            "cover_image": book.cover_image,
            "featured": book.featured,
            "author": author_name
        })


    return jsonify({
        "success": True,
        "query": query,
        "count": len(results),
        "results": results
    })
