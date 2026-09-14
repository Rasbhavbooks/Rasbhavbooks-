# =========================================================
# RASBHAV BOOKS
# PUBLIC CATEGORY ROUTES / API
# =========================================================
#
# PUBLIC WEBSITE
#       ↓
# CATEGORY API
#       ↓
# DATABASE
#
# Features:
# - Public category list
# - Category details
# - Published books only
# - Category books
# - Parent category information
# - Child categories
# - Book count
# - Safe JSON serialization
# =========================================================


from flask import Blueprint, jsonify

from app.models.category import Category
from app.models.book import Book
from app.models.book_categories import BookCategory


# =========================================================
# BLUEPRINT
# =========================================================

category_bp = Blueprint(
    "category",
    __name__,
    url_prefix="/api/categories"
)


# =========================================================
# CATEGORY SERIALIZER
# =========================================================

def category_to_dict(category):
    """
    Convert Category model into safe public JSON.
    """

    parent = None

    if category.parent:

        parent = {
            "id": category.parent.id,
            "name": category.parent.name,
            "slug": category.parent.slug
        }

    children = []

    for child in sorted(
        category.children,
        key=lambda item: (
            item.name or ""
        ).lower()
    ):

        children.append({

            "id":
                child.id,

            "name":
                child.name,

            "slug":
                child.slug,

            "description":
                child.description,

            "image":
                child.image,

            "parent_id":
                child.parent_id

        })

    return {

        "id":
            category.id,

        "name":
            category.name,

        "slug":
            category.slug,

        "description":
            category.description,

        "image":
            category.image,

        "parent_id":
            category.parent_id,

        "parent":
            parent,

        "children":
            children,

        "is_parent":
            len(children) > 0,

        "has_parent":
            category.parent_id is not None

    }


# =========================================================
# BOOK SERIALIZER
# =========================================================

def book_to_dict(book):
    """
    Convert Book model into safe public JSON.
    """

    author = None

    if book.author:

        author = {

            "id":
                book.author.id,

            "name":
                getattr(
                    book.author,
                    "name",
                    None
                ),

            "slug":
                getattr(
                    book.author,
                    "slug",
                    None
                )

        }

    return {

        "id":
            book.id,

        "title":
            book.title,

        "slug":
            book.slug,

        "subtitle":
            book.subtitle,

        "description":
            book.description,

        "short_description":
            book.short_description,

        "author_id":
            book.author_id,

        "author":
            author,

        "language":
            book.language,

        "tags":
            book.tags,

        "cover_image":
            book.cover_image,

        "banner_image":
            book.banner_image,

        "featured_image":
            book.featured_image,

        "status":
            book.status,

        "featured":
            bool(
                book.featured
            ),

        "published":
            bool(
                book.published
            ),

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


# =========================================================
# CATEGORY BOOK QUERY
# =========================================================

def get_published_category_books(category_id):
    """
    Return only published books belonging to a category.
    """

    return (
        Book.query

        .join(
            BookCategory,
            BookCategory.book_id == Book.id
        )

        .filter(

            BookCategory.category_id == category_id,

            Book.published.is_(True)

        )

        .order_by(

            Book.created_at.desc()

        )

        .all()
    )


# =========================================================
# GET ALL CATEGORIES
# =========================================================

@category_bp.route(
    "",
    methods=["GET"]
)
@category_bp.route(
    "/",
    methods=["GET"]
)
def get_categories():

    try:

        categories = (
            Category.query

            .order_by(
                Category.name.asc()
            )

            .all()
        )

        return jsonify({

            "success":
                True,

            "count":
                len(categories),

            "categories": [

                category_to_dict(
                    category
                )

                for category in categories

            ]

        }), 200

    except Exception as error:

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load categories.",

            "error":
                str(error)

        }), 500


# =========================================================
# GET SINGLE CATEGORY
# =========================================================

@category_bp.route(
    "/<string:slug>",
    methods=["GET"]
)
def get_category(slug):

    try:

        category = (
            Category.query

            .filter_by(
                slug=slug
            )

            .first()
        )

        if not category:

            return jsonify({

                "success":
                    False,

                "message":
                    "Category not found."

            }), 404

        books = get_published_category_books(
            category.id
        )

        data = category_to_dict(
            category
        )

        data["books"] = [

            book_to_dict(book)

            for book in books

        ]

        data["book_count"] = len(
            books
        )

        return jsonify({

            "success":
                True,

            "category":
                data

        }), 200

    except Exception as error:

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load category.",

            "error":
                str(error)

        }), 500


# =========================================================
# GET CATEGORY BOOKS
# =========================================================

@category_bp.route(
    "/<string:slug>/books",
    methods=["GET"]
)
def get_category_books(slug):

    try:

        category = (
            Category.query

            .filter_by(
                slug=slug
            )

            .first()
        )

        if not category:

            return jsonify({

                "success":
                    False,

                "message":
                    "Category not found."

            }), 404

        books = get_published_category_books(
            category.id
        )

        return jsonify({

            "success":
                True,

            "category":
                category_to_dict(
                    category
                ),

            "count":
                len(books),

            "books": [

                book_to_dict(book)

                for book in books

            ]

        }), 200

    except Exception as error:

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load category books.",

            "error":
                str(error)

        }), 500
