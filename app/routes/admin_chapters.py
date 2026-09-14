# ============================================================
# RASBHAV BOOKS
# ADMIN CHAPTER ROUTES / API
# ============================================================
#
# ADMIN PANEL
#      ↓
# ADMIN CHAPTER API
#      ↓
# DATABASE
#      ↓
# READER
#
# Features:
# - Admin authentication
# - Chapter CRUD
# - Book validation
# - Chapter number validation
# - Slug validation
# - Draft / Published / Private
# - Publish date
# - Reorder chapters
# - Safe JSON responses
# - Database rollback
# ============================================================


from flask import Blueprint, request, jsonify

from datetime import datetime

from app import db

from app.models.book import Book
from app.models.chapter import Chapter

from app.routes.admin import admin_required


# ============================================================
# BLUEPRINT
# ============================================================

admin_chapters_bp = Blueprint(
    "admin_chapters",
    __name__,
    url_prefix="/api/admin/chapters"
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


def parse_int(value, default=None):

    if value is None:
        return default

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def parse_bool(value, default=False):

    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        return bool(value)

    if isinstance(value, str):

        value = value.strip().lower()

        if value in (
            "true",
            "1",
            "yes",
            "on",
            "enabled"
        ):
            return True

        if value in (
            "false",
            "0",
            "no",
            "off",
            "disabled"
        ):
            return False

    return default


def parse_datetime(value):

    if not value:
        return None

    if isinstance(value, datetime):
        return value

    try:

        return datetime.fromisoformat(
            str(value).replace(
                "Z",
                "+00:00"
            )
        )

    except (
        ValueError,
        TypeError
    ):

        raise ValueError(
            "Invalid publish_date format."
        )


# ============================================================
# STATUS VALIDATION
# ============================================================

ALLOWED_STATUSES = (
    "draft",
    "published",
    "private"
)


def validate_status(status):

    status = clean_string(
        status,
        "draft"
    )

    if status not in ALLOWED_STATUSES:

        raise ValueError(
            "Invalid chapter status."
        )

    return status


# ============================================================
# BOOK SERIALIZER
# ============================================================

def book_to_dict(book):

    if not book:
        return None

    return {

        "id":
            book.id,

        "title":
            book.title,

        "slug":
            book.slug,

        "language":
            book.language
    }


# ============================================================
# CHAPTER SERIALIZER
# ============================================================

def chapter_to_dict(chapter):

    return {

        "id":
            chapter.id,

        "book_id":
            chapter.book_id,

        "book":
            book_to_dict(chapter.book),

        "chapter_number":
            chapter.chapter_number,

        "title":
            chapter.title,

        "slug":
            chapter.slug,

        "content":
            chapter.content,

        "status":
            chapter.status,

        "published":
            bool(chapter.published),

        "publish_date": (

            chapter.publish_date.isoformat()

            if chapter.publish_date

            else None
        ),

        "created_at": (

            chapter.created_at.isoformat()

            if chapter.created_at

            else None
        ),

        "updated_at": (

            chapter.updated_at.isoformat()

            if chapter.updated_at

            else None
        )
    }


# ============================================================
# GET ALL CHAPTERS
# ============================================================

@admin_chapters_bp.route(
    "",
    methods=["GET"]
)
@admin_chapters_bp.route(
    "/",
    methods=["GET"]
)
def get_chapters():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        query = Chapter.query

        # ----------------------------------------------------
        # BOOK FILTER
        # ----------------------------------------------------

        book_id = request.args.get(
            "book_id",
            type=int
        )

        if book_id:

            query = query.filter(
                Chapter.book_id == book_id
            )

        # ----------------------------------------------------
        # STATUS FILTER
        # ----------------------------------------------------

        status = clean_string(
            request.args.get("status")
        )

        if status:

            query = query.filter(
                Chapter.status == status
            )

        # ----------------------------------------------------
        # PUBLISHED FILTER
        # ----------------------------------------------------

        if "published" in request.args:

            published = parse_bool(
                request.args.get(
                    "published"
                )
            )

            query = query.filter(
                Chapter.published == published
            )

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        search = clean_string(
            request.args.get("search")
        )

        if search:

            pattern = f"%{search}%"

            query = query.filter(
                db.or_(
                    Chapter.title.ilike(pattern),
                    Chapter.slug.ilike(pattern),
                    Chapter.content.ilike(pattern)
                )
            )

        # ----------------------------------------------------
        # LIMIT
        # ----------------------------------------------------

        limit = parse_int(
            request.args.get("limit"),
            200
        )

        if limit < 1:
            limit = 1

        if limit > 500:
            limit = 500

        chapters = (
            query
            .order_by(
                Chapter.book_id.asc(),
                Chapter.chapter_number.asc(),
                Chapter.id.asc()
            )
            .limit(limit)
            .all()
        )

        return jsonify({

            "success":
                True,

            "count":
                len(chapters),

            "chapters": [
                chapter_to_dict(
                    chapter
                )
                for chapter in chapters
            ]

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load chapters.",

            "error":
                str(error)

        }), 500


# ============================================================
# GET SINGLE CHAPTER
# ============================================================

@admin_chapters_bp.route(
    "/<int:chapter_id>",
    methods=["GET"]
)
def get_chapter(chapter_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        chapter = Chapter.query.get(
            chapter_id
        )

        if not chapter:

            return jsonify({

                "success":
                    False,

                "message":
                    "Chapter not found."

            }), 404

        return jsonify({

            "success":
                True,

            "chapter":
                chapter_to_dict(
                    chapter
                )

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load chapter.",

            "error":
                str(error)

        }), 500


# ============================================================
# CREATE CHAPTER
# ============================================================

@admin_chapters_bp.route(
    "",
    methods=["POST"]
)
@admin_chapters_bp.route(
    "/",
    methods=["POST"]
)
def create_chapter():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(
        silent=True
    ) or {}

    try:

        # ----------------------------------------------------
        # BOOK
        # ----------------------------------------------------

        book_id = parse_int(
            data.get("book_id")
        )

        if not book_id:

            return jsonify({

                "success":
                    False,

                "message":
                    "Book is required."

            }), 400

        book = Book.query.get(
            book_id
        )

        if not book:

            return jsonify({

                "success":
                    False,

                "message":
                    "Book not found."

            }), 404

        # ----------------------------------------------------
        # CHAPTER NUMBER
        # ----------------------------------------------------

        chapter_number = parse_int(
            data.get("chapter_number")
        )

        if chapter_number is None:

            return jsonify({

                "success":
                    False,

                "message":
                    "Chapter number is required."

            }), 400

        if chapter_number < 1:

            return jsonify({

                "success":
                    False,

                "message":
                    "Chapter number must be greater than 0."

            }), 400

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = clean_string(
            data.get("title")
        )

        if not title:

            return jsonify({

                "success":
                    False,

                "message":
                    "Chapter title is required."

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
                    "Chapter slug is required."

            }), 400

        existing_slug = (
            Chapter.query
            .filter_by(slug=slug)
            .first()
        )

        if existing_slug:

            return jsonify({

                "success":
                    False,

                "message":
                    "Chapter slug already exists."

            }), 409

        # ----------------------------------------------------
        # CHAPTER NUMBER UNIQUE PER BOOK
        # ----------------------------------------------------

        existing_number = (
            Chapter.query
            .filter_by(
                book_id=book_id,
                chapter_number=chapter_number
            )
            .first()
        )

        if existing_number:

            return jsonify({

                "success":
                    False,

                "message":
                    "Chapter number already exists for this book."

            }), 409

        # ----------------------------------------------------
        # CONTENT
        # ----------------------------------------------------

        content = data.get(
            "content"
        )

        if content is None:
            content = ""

        content = str(
            content
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        status = validate_status(
            data.get("status")
        )

        # ----------------------------------------------------
        # PUBLISHED
        # ----------------------------------------------------

        published = parse_bool(
            data.get(
                "published"
            ),
            status == "published"
        )

        if status == "published":
            published = True

        if status in (
            "draft",
            "private"
        ):
            published = False

        # ----------------------------------------------------
        # PUBLISH DATE
        # ----------------------------------------------------

        publish_date = parse_datetime(
            data.get("publish_date")
        )

        # ----------------------------------------------------
        # CREATE
        # ----------------------------------------------------

        chapter = Chapter(

            book_id=book_id,

            chapter_number=chapter_number,

            title=title,

            slug=slug,

            content=content,

            status=status,

            published=published,

            publish_date=publish_date
        )

        db.session.add(
            chapter
        )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Chapter created successfully.",

            "chapter":
                chapter_to_dict(
                    chapter
                )

        }), 201

    except ValueError as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                str(error)

        }), 400

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to create chapter.",

            "error":
                str(error)

        }), 500


# ============================================================
# UPDATE CHAPTER
# ============================================================

@admin_chapters_bp.route(
    "/<int:chapter_id>",
    methods=["PUT", "PATCH"]
)
def update_chapter(chapter_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(
        silent=True
    ) or {}

    try:

        chapter = Chapter.query.get(
            chapter_id
        )

        if not chapter:

            return jsonify({

                "success":
                    False,

                "message":
                    "Chapter not found."

            }), 404

        # ----------------------------------------------------
        # BOOK
        # ----------------------------------------------------

        if "book_id" in data:

            new_book_id = parse_int(
                data.get("book_id")
            )

            if not new_book_id:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Invalid book_id."

                }), 400

            book = Book.query.get(
                new_book_id
            )

            if not book:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Book not found."

                }), 404

            chapter.book_id = new_book_id

        # ----------------------------------------------------
        # CHAPTER NUMBER
        # ----------------------------------------------------

        if "chapter_number" in data:

            new_number = parse_int(
                data.get(
                    "chapter_number"
                )
            )

            if new_number is None:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Invalid chapter number."

                }), 400

            if new_number < 1:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Chapter number must be greater than 0."

                }), 400

            existing_number = (
                Chapter.query
                .filter(
                    Chapter.book_id == chapter.book_id,
                    Chapter.chapter_number == new_number,
                    Chapter.id != chapter.id
                )
                .first()
            )

            if existing_number:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Chapter number already exists for this book."

                }), 409

            chapter.chapter_number = new_number

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        if "title" in data:

            title = clean_string(
                data.get("title")
            )

            if not title:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Chapter title cannot be empty."

                }), 400

            chapter.title = title

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
                        "Chapter slug cannot be empty."

                }), 400

            existing_slug = (
                Chapter.query
                .filter(
                    Chapter.slug == slug,
                    Chapter.id != chapter.id
                )
                .first()
            )

            if existing_slug:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Chapter slug already exists."

                }), 409

            chapter.slug = slug

        # ----------------------------------------------------
        # CONTENT
        # ----------------------------------------------------

        if "content" in data:

            content = data.get(
                "content"
            )

            chapter.content = (
                ""
                if content is None
                else str(content)
            )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        if "status" in data:

            status = validate_status(
                data.get("status")
            )

            chapter.status = status

            if status == "published":

                chapter.published = True

            elif status in (
                "draft",
                "private"
            ):

                chapter.published = False

        # ----------------------------------------------------
        # PUBLISHED
        # ----------------------------------------------------

        if "published" in data:

            chapter.published = parse_bool(
                data.get("published"),
                chapter.published
            )

            if chapter.published:

                chapter.status = "published"

            elif chapter.status == "published":

                chapter.status = "draft"

        # ----------------------------------------------------
        # PUBLISH DATE
        # ----------------------------------------------------

        if "publish_date" in data:

            chapter.publish_date = parse_datetime(
                data.get(
                    "publish_date"
                )
            )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Chapter updated successfully.",

            "chapter":
                chapter_to_dict(
                    chapter
                )

        }), 200

    except ValueError as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                str(error)

        }), 400

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to update chapter.",

            "error":
                str(error)

        }), 500


# ============================================================
# DELETE CHAPTER
# ============================================================

@admin_chapters_bp.route(
    "/<int:chapter_id>",
    methods=["DELETE"]
)
def delete_chapter(chapter_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        chapter = Chapter.query.get(
            chapter_id
        )

        if not chapter:

            return jsonify({

                "success":
                    False,

                "message":
                    "Chapter not found."

            }), 404

        db.session.delete(
            chapter
        )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Chapter deleted successfully.",

            "chapter_id":
                chapter_id

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to delete chapter.",

            "error":
                str(error)

        }), 500


# ============================================================
# PUBLISH CHAPTER
# ============================================================

@admin_chapters_bp.route(
    "/<int:chapter_id>/publish",
    methods=["POST"]
)
def publish_chapter(chapter_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        chapter = Chapter.query.get(
            chapter_id
        )

        if not chapter:

            return jsonify({

                "success":
                    False,

                "message":
                    "Chapter not found."

            }), 404

        chapter.published = True
        chapter.status = "published"

        if not chapter.publish_date:

            chapter.publish_date = datetime.utcnow()

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Chapter published successfully.",

            "chapter":
                chapter_to_dict(
                    chapter
                )

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to publish chapter.",

            "error":
                str(error)

        }), 500


# ============================================================
# UNPUBLISH CHAPTER
# ============================================================

@admin_chapters_bp.route(
    "/<int:chapter_id>/unpublish",
    methods=["POST"]
)
def unpublish_chapter(chapter_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        chapter = Chapter.query.get(
            chapter_id
        )

        if not chapter:

            return jsonify({

                "success":
                    False,

                "message":
                    "Chapter not found."

            }), 404

        chapter.published = False
        chapter.status = "draft"

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Chapter moved to draft.",

            "chapter":
                chapter_to_dict(
                    chapter
                )

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to unpublish chapter.",

            "error":
                str(error)

        }), 500


# ============================================================
# REORDER CHAPTERS
# ============================================================

@admin_chapters_bp.route(
    "/reorder",
    methods=["POST"]
)
def reorder_chapters():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(
        silent=True
    ) or {}

    chapters = data.get(
        "chapters",
        []
    )

    if not isinstance(
        chapters,
        list
    ):

        return jsonify({

            "success":
                False,

            "message":
                "Chapters must be a list."

        }), 400

    try:

        # ----------------------------------------------------
        # FIRST VALIDATE ALL ITEMS
        # ----------------------------------------------------

        updates = []

        for item in chapters:

            if not isinstance(
                item,
                dict
            ):
                continue

            chapter_id = parse_int(
                item.get("id")
            )

            position = parse_int(
                item.get(
                    "chapter_number"
                )
            )

            if chapter_id is None:
                continue

            if position is None:
                continue

            if position < 1:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Chapter number must be greater than 0."

                }), 400

            chapter = Chapter.query.get(
                chapter_id
            )

            if not chapter:

                return jsonify({

                    "success":
                        False,

                    "message":
                        f"Chapter {chapter_id} not found."

                }), 404

            updates.append(
                (
                    chapter,
                    position
                )
            )

        # ----------------------------------------------------
        # CHECK DUPLICATES PER BOOK
        # ----------------------------------------------------

        grouped = {}

        for chapter, position in updates:

            grouped.setdefault(
                chapter.book_id,
                []
            ).append(
                position
            )

        for book_id, positions in grouped.items():

            if len(positions) != len(
                set(positions)
            ):

                return jsonify({

                    "success":
                        False,

                    "message":
                        f"Duplicate chapter numbers found for book {book_id}."

                }), 409

        # ----------------------------------------------------
        # APPLY
        # ----------------------------------------------------

        for chapter, position in updates:

            chapter.chapter_number = position

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Chapters reordered successfully."

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to reorder chapters.",

            "error":
                str(error)

        }), 500
