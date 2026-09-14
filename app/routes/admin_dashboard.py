# =========================================================
# RASBHAV BOOKS
# ADMIN DASHBOARD ROUTES
# =========================================================

from flask import Blueprint, jsonify, session

from app.models.book import Book
from app.models.chapter import Chapter
from app.models.user import User
from app.models.author import Author
from app.models.category import Category
from app.models.page import Page
from app.models.media import Media
from app.models.widget import Widget
from app.models.layout_section import LayoutSection


# =========================================================
# BLUEPRINT
# =========================================================

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
# SAFE COUNT HELPER
# =========================================================

def safe_count(model):
    try:
        return model.query.count()
    except Exception:
        return 0


# =========================================================
# RECENT BOOK SERIALIZER
# =========================================================

def recent_book_to_dict(book):
    return {
        "id": book.id,
        "title": book.title,
        "slug": book.slug,
        "language": book.language,
        "cover_image": book.cover_image,
        "published": bool(book.published),
        "featured": bool(book.featured),
        "status": book.status,
        "created_at": (
            book.created_at.isoformat()
            if book.created_at
            else None
        ),
        "updated_at": (
            book.updated_at.isoformat()
            if book.updated_at
            else None
        )
    }


# =========================================================
# DASHBOARD STATS
# =========================================================

@admin_dashboard_bp.route("", methods=["GET"])
@admin_dashboard_bp.route("/", methods=["GET"])
@admin_dashboard_bp.route("/stats", methods=["GET"])
def dashboard():

    # -----------------------------------------------------
    # AUTH
    # -----------------------------------------------------

    if not admin_required():
        return jsonify({
            "success": False,
            "message": "Admin login required."
        }), 401

    # -----------------------------------------------------
    # BOOKS
    # -----------------------------------------------------

    total_books = safe_count(Book)

    published_books = (
        Book.query
        .filter(Book.published.is_(True))
        .count()
    )

    draft_books = (
        Book.query
        .filter(Book.published.is_(False))
        .count()
    )

    featured_books = (
        Book.query
        .filter(Book.featured.is_(True))
        .count()
    )

    # -----------------------------------------------------
    # CHAPTERS
    # -----------------------------------------------------

    total_chapters = safe_count(Chapter)

    published_chapters = (
        Chapter.query
        .filter(Chapter.published.is_(True))
        .count()
    )

    draft_chapters = (
        Chapter.query
        .filter(Chapter.published.is_(False))
        .count()
    )

    # -----------------------------------------------------
    # USERS
    # -----------------------------------------------------

    total_users = safe_count(User)

    active_users = (
        User.query
        .filter(User.is_active.is_(True))
        .count()
    )

    inactive_users = (
        User.query
        .filter(User.is_active.is_(False))
        .count()
    )

    # -----------------------------------------------------
    # AUTHORS
    # -----------------------------------------------------

    total_authors = safe_count(Author)

    # -----------------------------------------------------
    # CATEGORIES
    # -----------------------------------------------------

    total_categories = safe_count(Category)

    # -----------------------------------------------------
    # CMS
    # -----------------------------------------------------

    total_pages = safe_count(Page)
    total_media = safe_count(Media)
    total_widgets = safe_count(Widget)
    total_layout_sections = safe_count(LayoutSection)

    active_widgets = (
        Widget.query
        .filter(Widget.is_active.is_(True))
        .count()
    )

    active_layout_sections = (
        LayoutSection.query
        .filter(LayoutSection.is_active.is_(True))
        .count()
    )

    # -----------------------------------------------------
    # RECENT BOOKS
    # -----------------------------------------------------

    recent_books = (
        Book.query
        .order_by(Book.created_at.desc())
        .limit(10)
        .all()
    )

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return jsonify({

        "success": True,

        "stats": {

            # Books
            "total_books": total_books,
            "published_books": published_books,
            "draft_books": draft_books,
            "featured_books": featured_books,

            # Chapters
            "total_chapters": total_chapters,
            "published_chapters": published_chapters,
            "draft_chapters": draft_chapters,

            # Users
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,

            # Authors / Categories
            "total_authors": total_authors,
            "total_categories": total_categories,

            # CMS
            "total_pages": total_pages,
            "total_media": total_media,
            "total_widgets": total_widgets,
            "total_layout_sections": total_layout_sections,

            # Active UI
            "active_widgets": active_widgets,
            "active_layout_sections": active_layout_sections
        },

        "recent_books": [
            recent_book_to_dict(book)
            for book in recent_books
        ]

    }), 200
