# =========================================================
# RASBHAV BOOKS
# CATEGORY ROUTES
# Flask + SQLite
# =========================================================

from flask import Blueprint, jsonify

from app.models.category import Category
from app.models.book import Book


# =========================================================
# BLUEPRINT
# =========================================================

category_bp = Blueprint(
    "category",
    __name__,
    url_prefix="/api/categories"
)


# =========================================================
# HELPER
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


def book_to_dict(book):
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
        "featured": bool(book.featured),
        "published": bool(book.published),
        "publish_date": (
            book.publish_date.isoformat()
            if book.publish_date
            else None
        )
    }


# =========================================================
# GET ALL CATEGORIES
# =========================================================

@category_bp.route("", methods=["GET"])
def get_categories():

    categories = Category.query.order_by(
        Category.name.asc()
    ).all()

    return jsonify([
        category_to_dict(category)
        for category in categories
    ])


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
        **category_to_dict(category),

        "books": [
            book_to_dict(book)
            for book in books
        ],

        "book_count": len(books)
    })


# =========================================================
# GET CATEGORY BOOKS
# =========================================================

@category_bp.route("/<slug>/books", methods=["GET"])
def get_category_books(slug):

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
        "category": category_to_dict(category),
        "count": len(books),
        "books": [
            book_to_dict(book)
            for book in books
        ]
    })
