# ============================================================
# RASBHAV BOOKS
# ADMIN DASHBOARD ROUTES / API
# ============================================================
#
# ADMIN PANEL
#      ↓
# DASHBOARD API
#      ↓
# DATABASE
#
# Dashboard includes:
# - Books
# - Chapters
# - Users
# - Authors
# - Categories
# - Pages
# - Media
# - SEO
# - Site Settings
# - Menus
# - Menu Items
# - Widgets
# - Layout Sections
# - Recent Books
# - Recent Media
# - Recent Users
# ============================================================


from flask import (
    Blueprint,
    jsonify,
)

from app import db

from app.models.book import Book
from app.models.chapter import Chapter
from app.models.user import User
from app.models.author import Author
from app.models.category import Category
from app.models.page import Page
from app.models.media import Media
from app.models.widget import Widget
from app.models.layout_section import LayoutSection
from app.models.seo import SEO
from app.models.site_setting import SiteSetting
from app.models.menu import Menu
from app.models.menu_item import MenuItem

from app.routes.admin import admin_required


# ============================================================
# BLUEPRINT
# ============================================================

admin_dashboard_bp = Blueprint(
    "admin_dashboard",
    __name__,
    url_prefix="/api/admin/dashboard"
)


# ============================================================
# SAFE COUNT
# ============================================================

def safe_count(model):

    try:
        return model.query.count()

    except Exception:
        return 0


# ============================================================
# SAFE FILTER COUNT
# ============================================================

def safe_filter_count(
    model,
    condition
):

    try:
        return (
            model.query
            .filter(condition)
            .count()
        )

    except Exception:
        return 0


# ============================================================
# BOOK SERIALIZER
# ============================================================

def recent_book_to_dict(book):

    return {

        "id":
            book.id,

        "title":
            book.title,

        "slug":
            book.slug,

        "language":
            book.language,

        "cover_image":
            book.cover_image,

        "featured_image":
            book.featured_image,

        "published":
            bool(book.published),

        "featured":
            bool(book.featured),

        "status":
            book.status,

        "publish_date": (
            book.publish_date.isoformat()
            if book.publish_date
            else None
        ),

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


# ============================================================
# MEDIA SERIALIZER
# ============================================================

def recent_media_to_dict(media):

    return {

        "id":
            media.id,

        "filename":
            media.get_filename(),

        "url":
            media.get_url(),

        "file_type":
            media.get_file_type(),

        "mime_type":
            media.get_mime_type(),

        "file_size":
            media.file_size,

        "file_size_mb":
            media.get_file_size_mb(),

        "alt_text":
            media.alt_text,

        "width":
            media.width,

        "height":
            media.height,

        "is_image":
            media.is_image(),

        "created_at": (
            media.created_at.isoformat()
            if media.created_at
            else None
        )
    }


# ============================================================
# USER SERIALIZER
# ============================================================

def recent_user_to_dict(user):

    return {

        "id":
            user.id,

        "username":
            user.username,

        "email":
            user.email,

        "full_name":
            user.full_name,

        "is_active":
            bool(user.is_active),

        "created_at": (
            user.created_at.isoformat()
            if user.created_at
            else None
        )
    }


# ============================================================
# DASHBOARD DATA
# ============================================================

def build_dashboard_data():

    # ========================================================
    # BOOKS
    # ========================================================

    total_books = safe_count(
        Book
    )

    published_books = safe_filter_count(
        Book,
        Book.published.is_(True)
    )

    draft_books = safe_filter_count(
        Book,
        Book.published.is_(False)
    )

    featured_books = safe_filter_count(
        Book,
        Book.featured.is_(True)
    )

    # ========================================================
    # CHAPTERS
    # ========================================================

    total_chapters = safe_count(
        Chapter
    )

    published_chapters = safe_filter_count(
        Chapter,
        Chapter.published.is_(True)
    )

    draft_chapters = safe_filter_count(
        Chapter,
        Chapter.published.is_(False)
    )

    # ========================================================
    # USERS
    # ========================================================

    total_users = safe_count(
        User
    )

    active_users = safe_filter_count(
        User,
        User.is_active.is_(True)
    )

    inactive_users = safe_filter_count(
        User,
        User.is_active.is_(False)
    )

    # ========================================================
    # AUTHORS
    # ========================================================

    total_authors = safe_count(
        Author
    )

    # ========================================================
    # CATEGORIES
    # ========================================================

    total_categories = safe_count(
        Category
    )

    parent_categories = safe_filter_count(
        Category,
        Category.parent_id.is_(None)
    )

    child_categories = safe_filter_count(
        Category,
        Category.parent_id.isnot(None)
    )

    # ========================================================
    # PAGES
    # ========================================================

    total_pages = safe_count(
        Page
    )

    published_pages = safe_filter_count(
        Page,
        Page.status == "published"
    )

    draft_pages = safe_filter_count(
        Page,
        Page.status == "draft"
    )

    private_pages = safe_filter_count(
        Page,
        Page.status == "private"
    )

    # ========================================================
    # MEDIA
    # ========================================================

    total_media = safe_count(
        Media
    )

    image_media = safe_filter_count(
        Media,
        Media.mime_type.ilike(
            "image/%"
        )
    )

    video_media = safe_filter_count(
        Media,
        Media.mime_type.ilike(
            "video/%"
        )
    )

    # ========================================================
    # SEO
    # ========================================================

    total_seo = safe_count(
        SEO
    )

    book_seo = safe_filter_count(
        SEO,
        SEO.entity_type == "book"
    )

    chapter_seo = safe_filter_count(
        SEO,
        SEO.entity_type == "chapter"
    )

    category_seo = safe_filter_count(
        SEO,
        SEO.entity_type == "category"
    )

    author_seo = safe_filter_count(
        SEO,
        SEO.entity_type == "author"
    )

    page_seo = safe_filter_count(
        SEO,
        SEO.entity_type == "page"
    )

    home_seo = safe_filter_count(
        SEO,
        SEO.entity_type == "home"
    )

    site_seo = safe_filter_count(
        SEO,
        SEO.entity_type == "site"
    )

    # ========================================================
    # SETTINGS
    # ========================================================

    total_settings = safe_count(
        SiteSetting
    )

    # ========================================================
    # MENUS
    # ========================================================

    total_menus = safe_count(
        Menu
    )

    active_menus = safe_filter_count(
        Menu,
        Menu.is_active.is_(True)
    )

    total_menu_items = safe_count(
        MenuItem
    )

    active_menu_items = safe_filter_count(
        MenuItem,
        MenuItem.is_active.is_(True)
    )

    # ========================================================
    # WIDGETS
    # ========================================================

    total_widgets = safe_count(
        Widget
    )

    active_widgets = safe_filter_count(
        Widget,
        Widget.is_active.is_(True)
    )

    inactive_widgets = safe_filter_count(
        Widget,
        Widget.is_active.is_(False)
    )

    # ========================================================
    # LAYOUT SECTIONS
    # ========================================================

    total_layout_sections = safe_count(
        LayoutSection
    )

    active_layout_sections = safe_filter_count(
        LayoutSection,
        LayoutSection.is_active.is_(True)
    )

    inactive_layout_sections = safe_filter_count(
        LayoutSection,
        LayoutSection.is_active.is_(False)
    )

    # ========================================================
    # RECENT BOOKS
    # ========================================================

    try:

        recent_books = (
            Book.query
            .order_by(
                Book.created_at.desc(),
                Book.id.desc()
            )
            .limit(10)
            .all()
        )

    except Exception:

        recent_books = []

    # ========================================================
    # RECENT MEDIA
    # ========================================================

    try:

        recent_media = (
            Media.query
            .order_by(
                Media.created_at.desc(),
                Media.id.desc()
            )
            .limit(10)
            .all()
        )

    except Exception:

        recent_media = []

    # ========================================================
    # RECENT USERS
    # ========================================================

    try:

        recent_users = (
            User.query
            .order_by(
                User.created_at.desc(),
                User.id.desc()
            )
            .limit(10)
            .all()
        )

    except Exception:

        recent_users = []

    # ========================================================
    # RETURN
    # ========================================================

    return {

        "books": {

            "total":
                total_books,

            "published":
                published_books,

            "draft":
                draft_books,

            "featured":
                featured_books
        },

        "chapters": {

            "total":
                total_chapters,

            "published":
                published_chapters,

            "draft":
                draft_chapters
        },

        "users": {

            "total":
                total_users,

            "active":
                active_users,

            "inactive":
                inactive_users
        },

        "authors": {

            "total":
                total_authors
        },

        "categories": {

            "total":
                total_categories,

            "parents":
                parent_categories,

            "children":
                child_categories
        },

        "pages": {

            "total":
                total_pages,

            "published":
                published_pages,

            "draft":
                draft_pages,

            "private":
                private_pages
        },

        "media": {

            "total":
                total_media,

            "images":
                image_media,

            "videos":
                video_media
        },

        "seo": {

            "total":
                total_seo,

            "book":
                book_seo,

            "chapter":
                chapter_seo,

            "category":
                category_seo,

            "author":
                author_seo,

            "page":
                page_seo,

            "home":
                home_seo,

            "site":
                site_seo
        },

        "settings": {

            "total":
                total_settings
        },

        "menus": {

            "total":
                total_menus,

            "active":
                active_menus
        },

        "menu_items": {

            "total":
                total_menu_items,

            "active":
                active_menu_items
        },

        "widgets": {

            "total":
                total_widgets,

            "active":
                active_widgets,

            "inactive":
                inactive_widgets
        },

        "layout_sections": {

            "total":
                total_layout_sections,

            "active":
                active_layout_sections,

            "inactive":
                inactive_layout_sections
        },

        # ----------------------------------------------------
        # BACKWARD COMPATIBILITY
        # ----------------------------------------------------

        "total_books":
            total_books,

        "published_books":
            published_books,

        "draft_books":
            draft_books,

        "featured_books":
            featured_books,

        "total_chapters":
            total_chapters,

        "published_chapters":
            published_chapters,

        "draft_chapters":
            draft_chapters,

        "total_users":
            total_users,

        "active_users":
            active_users,

        "inactive_users":
            inactive_users,

        "total_authors":
            total_authors,

        "total_categories":
            total_categories,

        "total_pages":
            total_pages,

        "total_media":
            total_media,

        "total_widgets":
            total_widgets,

        "total_layout_sections":
            total_layout_sections,

        "active_widgets":
            active_widgets,

        "active_layout_sections":
            active_layout_sections
    }, recent_books, recent_media, recent_users


# ============================================================
# DASHBOARD
# ============================================================

@admin_dashboard_bp.route(
    "",
    methods=["GET"]
)
@admin_dashboard_bp.route(
    "/",
    methods=["GET"]
)
@admin_dashboard_bp.route(
    "/stats",
    methods=["GET"]
)
def dashboard():

    # --------------------------------------------------------
    # AUTH
    # --------------------------------------------------------

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        (
            stats,
            recent_books,
            recent_media,
            recent_users
        ) = build_dashboard_data()

        # ----------------------------------------------------
        # CURRENT ADMIN
        # ----------------------------------------------------

        from app.routes.admin import get_current_admin

        admin = get_current_admin()

        admin_data = None

        if admin:

            admin_data = {

                "id":
                    admin.id,

                "username":
                    admin.username,

                "email":
                    admin.email,

                "full_name":
                    admin.full_name,

                "is_active":
                    bool(
                        admin.is_active
                    ),

                "is_super_admin":
                    bool(
                        admin.is_super_admin
                    )
            }

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return jsonify({

            "success":
                True,

            "authenticated":
                True,

            "admin":
                admin_data,

            "stats":
                stats,

            "recent_books":
                [
                    recent_book_to_dict(
                        book
                    )
                    for book in recent_books
                ],

            "recent_media":
                [
                    recent_media_to_dict(
                        media
                    )
                    for media in recent_media
                ],

            "recent_users":
                [
                    recent_user_to_dict(
                        user
                    )
                    for user in recent_users
                ]

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load dashboard.",

            "error":
                str(error)

        }), 500
