from flask import Blueprint, request, jsonify
from app.models.book import Book

search_bp = Blueprint("search", __name__, url_prefix="/search")


@search_bp.route("/", methods=["GET"])
def search_books():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({
            "success": True,
            "query": "",
            "results": []
        })

    books = Book.query.filter(
        Book.title.ilike(f"%{query}%")
    ).all()

    results = []

    for book in books:
        results.append({
            "id": book.id,
            "title": book.title,
            "slug": book.slug
        })

    return jsonify({
        "success": True,
        "query": query,
        "count": len(results),
        "results": results
    })
