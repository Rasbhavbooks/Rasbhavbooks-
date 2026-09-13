from flask import Blueprint, jsonify, session

from app import db
from app.models.book import Book
from app.models.chapter import Chapter
from app.models.user import User
from app.models.author import Author
from app.models.category import Category


admin_dashboard_bp = Blueprint(
    "admin_dashboard",
    __name__,
    url_prefix="/api/admin/dashboard"
)


# =========================================================
# ADMIN AUTH CHECK
# =========================================================

def admin_required():
    return session.get("admin_logged_in") is True


# =========================================================
# DASHBOARD
# =========================================================

@admin_dashboard_bp.route("", methods=["GET"])
def dashboard():

    if not admin_required():
        return jsonify({
            "success": False,
            "message": "Admin login required."
        }), 401

    total_books = Book.query.count()

    published_books = Book.query.filter_by(
        published=True
    ).count()

    draft_books = Book.query.filter_by(
        published=False
    ).count()

    total_chapters = Chapter.query.count()

    published_chapters = Chapter.query.filter_by(
        status="published"
    ).count()

    draft_chapters = Chapter.query.filter_by(
        status="draft"
    ).count()

    total_users = User.query.count()

    active_users = User.query.filter_by(
        is_active=True
    ).count()

    total_authors = Author.query.count()

    total_categories = Category.query.count()

    recent_books = Book.query.order_by(
        Book.created_at.desc()
    ).limit(10).all()

    return jsonify({
        "success": True,

        "stats": {
            "total_books": total_books,
            "published_books": published_books,
            "draft_books": draft_books,

            "total_chapters": total_chapters,
            "published_chapters": published_chapters,
            "draft_chapters": draft_chapters,

            "total_users": total_users,
            "active_users": active_users,

            "total_authors": total_authors,
            "total_categories": total_categories
        },

        "recent_books": [
            {
                "id": book.id,
                "title": book.title,
                "slug": book.slug,
                "language": book.language,
                "cover_image": book.cover_image,
                "published": book.published,
                "featured": book.featured,
                "created_at": (
                    book.created_at.isoformat()
                    if book.created_at else None
                )
            }
            for book in recent_books
        ]
    })
