# ============================================================
# RASBHAV BOOKS
# ADMIN AUTHORS ROUTES / API
# ============================================================
#
# ADMIN PANEL
#      ↓
# AUTHOR API
#      ↓
# DATABASE
#      ↓
# PUBLIC WEBSITE
#
# Features:
# - Admin authentication
# - Author CRUD
# - Search
# - Slug validation
# - Biography
# - Profile image
# - Social links
# - Author books
# - Book count
# - Safe delete
# - Rollback on errors
# - Complete JSON responses
# ============================================================


from flask import Blueprint, request, jsonify

from app import db

from app.models.author import Author
from app.models.book import Book

from app.routes.admin import admin_required


# ============================================================
# BLUEPRINT
# ============================================================

admin_authors_bp = Blueprint(
    "admin_authors",
    __name__,
    url_prefix="/api/admin/authors"
)


# ============================================================
# HELPERS
# ============================================================

def clean_string(value, default=None):

    if value is None:
        return default

    value = str(value).strip()

    if not value:
        return default

    return value


# ============================================================
# AUTHOR SERIALIZER
# ============================================================

def author_to_dict(
    author,
    include_books=False
):

    data = {

        "id":
            author.id,

        "name":
            author.name,

        "slug":
            author.slug,

        "biography":
            author.biography,

        "profile_image":
            author.profile_image,

        "social_links":
            author.social_links,

        "display_name":
            author.get_display_name(),

        "has_biography":
            author.has_biography(),

        "has_profile_image":
            author.has_profile_image(),

        "created_at": (
            author.created_at.isoformat()
            if author.created_at
            else None
        ),

        "updated_at": (
            author.updated_at.isoformat()
            if author.updated_at
            else None
        )
    }

    # --------------------------------------------------------
    # BOOKS
    # --------------------------------------------------------

    if include_books:

        books = (
            Book.query
            .filter(
                Book.author_id == author.id
            )
            .order_by(
                Book.title.asc()
            )
            .all()
        )

        data["book_count"] = len(
            books
        )

        data["books"] = [

            {
                "id":
                    book.id,

                "title":
                    book.title,

                "slug":
                    book.slug,

                "subtitle":
                    book.subtitle,

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
                )
            }

            for book in books
        ]

    else:

        data["book_count"] = (
            Book.query
            .filter(
                Book.author_id == author.id
            )
            .count()
        )

    return data


# ============================================================
# GET ALL AUTHORS
# ============================================================

@admin_authors_bp.route(
    "",
    methods=["GET"]
)
@admin_authors_bp.route(
    "/",
    methods=["GET"]
)
def get_authors():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        query = Author.query

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        search = clean_string(
            request.args.get(
                "search"
            )
        )

        if search:

            pattern = f"%{search}%"

            query = query.filter(
                db.or_(
                    Author.name.ilike(
                        pattern
                    ),

                    Author.slug.ilike(
                        pattern
                    ),

                    Author.biography.ilike(
                        pattern
                    )
                )
            )

        # ----------------------------------------------------
        # LIMIT
        # ----------------------------------------------------

        limit_value = request.args.get(
            "limit"
        )

        if limit_value:

            try:
                limit = int(
                    limit_value
                )

            except (
                TypeError,
                ValueError
            ):

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Invalid limit."

                }), 400

        else:

            limit = 200

        if limit < 1:
            limit = 1

        if limit > 500:
            limit = 500

        # ----------------------------------------------------
        # FETCH
        # ----------------------------------------------------

        authors = (
            query
            .order_by(
                Author.name.asc()
            )
            .limit(limit)
            .all()
        )

        return jsonify({

            "success":
                True,

            "count":
                len(authors),

            "authors": [

                author_to_dict(
                    author
                )

                for author in authors
            ]

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load authors.",

            "error":
                str(error)

        }), 500


# ============================================================
# GET SINGLE AUTHOR
# ============================================================

@admin_authors_bp.route(
    "/<int:author_id>",
    methods=["GET"]
)
def get_author(author_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        author = Author.query.get(
            author_id
        )

        if not author:

            return jsonify({

                "success":
                    False,

                "message":
                    "Author not found."

            }), 404

        return jsonify({

            "success":
                True,

            "author":
                author_to_dict(
                    author,
                    include_books=True
                )

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load author.",

            "error":
                str(error)

        }), 500


# ============================================================
# GET AUTHOR BOOKS
# ============================================================

@admin_authors_bp.route(
    "/<int:author_id>/books",
    methods=["GET"]
)
def get_author_books(author_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        author = Author.query.get(
            author_id
        )

        if not author:

            return jsonify({

                "success":
                    False,

                "message":
                    "Author not found."

            }), 404

        books = (
            Book.query
            .filter(
                Book.author_id == author.id
            )
            .order_by(
                Book.title.asc()
            )
            .all()
        )

        return jsonify({

            "success":
                True,

            "author": {

                "id":
                    author.id,

                "name":
                    author.name,

                "slug":
                    author.slug
            },

            "count":
                len(books),

            "books": [

                {
                    "id":
                        book.id,

                    "title":
                        book.title,

                    "slug":
                        book.slug,

                    "subtitle":
                        book.subtitle,

                    "language":
                        book.language,

                    "cover_image":
                        book.cover_image,

                    "featured":
                        bool(book.featured),

                    "published":
                        bool(book.published),

                    "status":
                        book.status
                }

                for book in books
            ]

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load author books.",

            "error":
                str(error)

        }), 500


# ============================================================
# CREATE AUTHOR
# ============================================================

@admin_authors_bp.route(
    "",
    methods=["POST"]
)
@admin_authors_bp.route(
    "/",
    methods=["POST"]
)
def create_author():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(
        silent=True
    ) or {}

    try:

        # ----------------------------------------------------
        # NAME
        # ----------------------------------------------------

        name = clean_string(
            data.get("name")
        )

        if not name:

            return jsonify({

                "success":
                    False,

                "message":
                    "Author name is required."

            }), 400

        # ----------------------------------------------------
        # SLUG
        # ----------------------------------------------------

        slug = clean_string(
            data.get("slug")
        )

        if not slug:

            return jsonify({

                "success":
                    False,

                "message":
                    "Author slug is required."

            }), 400

        # ----------------------------------------------------
        # UNIQUE SLUG
        # ----------------------------------------------------

        existing = (
            Author.query
            .filter_by(
                slug=slug
            )
            .first()
        )

        if existing:

            return jsonify({

                "success":
                    False,

                "message":
                    "Author slug already exists."

            }), 409

        # ----------------------------------------------------
        # CREATE
        # ----------------------------------------------------

        author = Author(

            name=name,

            slug=slug,

            biography=clean_string(
                data.get(
                    "biography"
                )
            ),

            profile_image=clean_string(
                data.get(
                    "profile_image"
                )
            ),

            social_links=clean_string(
                data.get(
                    "social_links"
                )
            )
        )

        db.session.add(
            author
        )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Author created successfully.",

            "author":
                author_to_dict(
                    author,
                    include_books=True
                )

        }), 201

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to create author.",

            "error":
                str(error)

        }), 500


# ============================================================
# UPDATE AUTHOR
# ============================================================

@admin_authors_bp.route(
    "/<int:author_id>",
    methods=["PUT", "PATCH"]
)
def update_author(author_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(
        silent=True
    ) or {}

    try:

        author = Author.query.get(
            author_id
        )

        if not author:

            return jsonify({

                "success":
                    False,

                "message":
                    "Author not found."

            }), 404

        # ----------------------------------------------------
        # NAME
        # ----------------------------------------------------

        if "name" in data:

            name = clean_string(
                data.get("name")
            )

            if not name:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Author name cannot be empty."

                }), 400

            author.name = name

        # ----------------------------------------------------
        # SLUG
        # ----------------------------------------------------

        if "slug" in data:

            slug = clean_string(
                data.get("slug")
            )

            if not slug:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Author slug cannot be empty."

                }), 400

            existing = (
                Author.query
                .filter(
                    Author.slug == slug,
                    Author.id != author.id
                )
                .first()
            )

            if existing:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Author slug already exists."

                }), 409

            author.slug = slug

        # ----------------------------------------------------
        # BIOGRAPHY
        # ----------------------------------------------------

        if "biography" in data:

            author.biography = (
                clean_string(
                    data.get(
                        "biography"
                    )
                )
            )

        # ----------------------------------------------------
        # PROFILE IMAGE
        # ----------------------------------------------------

        if "profile_image" in data:

            author.profile_image = (
                clean_string(
                    data.get(
                        "profile_image"
                    )
                )
            )

        # ----------------------------------------------------
        # SOCIAL LINKS
        # ----------------------------------------------------

        if "social_links" in data:

            author.social_links = (
                clean_string(
                    data.get(
                        "social_links"
                    )
                )
            )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Author updated successfully.",

            "author":
                author_to_dict(
                    author,
                    include_books=True
                )

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to update author.",

            "error":
                str(error)

        }), 500


# ============================================================
# DELETE AUTHOR
# ============================================================

@admin_authors_bp.route(
    "/<int:author_id>",
    methods=["DELETE"]
)
def delete_author(author_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        author = Author.query.get(
            author_id
        )

        if not author:

            return jsonify({

                "success":
                    False,

                "message":
                    "Author not found."

            }), 404

        # ----------------------------------------------------
        # CHECK BOOKS
        # ----------------------------------------------------

        book_count = (
            Book.query
            .filter(
                Book.author_id == author.id
            )
            .count()
        )

        # ----------------------------------------------------
        # SAFE DELETE
        #
        # Books should not be deleted when an author is
        # deleted. Their author_id is simply cleared.
        # ----------------------------------------------------

        if book_count > 0:

            books = (
                Book.query
                .filter(
                    Book.author_id == author.id
                )
                .all()
            )

            for book in books:

                book.author_id = None

        db.session.delete(
            author
        )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Author deleted successfully.",

            "author_id":
                author_id,

            "books_unlinked":
                book_count

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to delete author.",

            "error":
                str(error)

        }), 500
