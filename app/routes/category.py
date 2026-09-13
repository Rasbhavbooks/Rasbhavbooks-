from flask import Blueprint, jsonify

from app.models.category import Category
from app.models.book import Book


category_bp = Blueprint(
    "category",
    __name__,
    url_prefix="/api/categories"
)


# =========================================================
# GET ALL CATEGORIES
# =========================================================

@category_bp.route("", methods=["GET"])
def get_categories():

    categories = Category.query.order_by(
        Category.name.asc()
    ).all()

    results = []

    for category in categories:

        results.append({
            "id": category.id,
            "name": category.name,
            "slug": category.slug,
            "description": category.description,
            "image": category.image,
            "parent_id": category.parent_id
        })

    return jsonify(results)


# =========================================================
# GET SINGLE CATEGORY
# =========================================================

@category_bp.route("/<slug>", methods=["GET"])
def get_category(slug):

    category = Category.query.filter_by(
        slug=slug
    ).first_or_404()

    books = Book.query.filter(
        Book.published.is_(True)
    ).filter(
        Book.categories.any(
            Category.id == category.id
        )
    ).order_by(
        Book.created_at.desc()
    ).all()

    return jsonify({
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "description": category.description,
        "image": category.image,
        "parent_id": category.parent_id,

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
