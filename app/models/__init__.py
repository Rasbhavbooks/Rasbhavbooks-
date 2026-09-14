# =========================================================
# RASBHAV BOOKS
# MODELS PACKAGE
# =========================================================
#
# Central model registry.
#
# All database models are imported here so Flask-SQLAlchemy
# can discover them when the application starts.
#
# Architecture:
#
# Flask App
#     ↓
# SQLAlchemy
#     ↓
# Models
#     ↓
# Database
#
# =========================================================


# =========================================================
# CORE CONTENT
# =========================================================

from app.models.book import Book
from app.models.chapter import Chapter
from app.models.category import Category
from app.models.author import Author
from app.models.book_categories import BookCategory


# =========================================================
# USERS & AUTHENTICATION
# =========================================================

from app.models.user import User
from app.models.admin import Admin


# =========================================================
# READING FEATURES
# =========================================================

from app.models.bookmark import Bookmark
from app.models.favorite import Favorite
from app.models.reading_progress import ReadingProgress


# =========================================================
# CMS
# =========================================================

from app.models.page import Page
from app.models.menu import Menu
from app.models.menu_item import MenuItem
from app.models.site_setting import SiteSetting


# =========================================================
# SEO
# =========================================================

from app.models.seo import SEO


# =========================================================
# MEDIA
# =========================================================

from app.models.media import Media


# =========================================================
# DYNAMIC UI / CMS
# =========================================================

from app.models.widget import Widget
from app.models.layout_section import LayoutSection


# =========================================================
# PUBLIC MODEL EXPORTS
# =========================================================

__all__ = [
    # Core content
    "Book",
    "Chapter",
    "Category",
    "Author",
    "BookCategory",

    # Authentication
    "User",
    "Admin",

    # Reading
    "Bookmark",
    "Favorite",
    "ReadingProgress",

    # CMS
    "Page",
    "Menu",
    "MenuItem",
    "SiteSetting",

    # SEO
    "SEO",

    # Media
    "Media",

    # Dynamic UI
    "Widget",
    "LayoutSection",
]
