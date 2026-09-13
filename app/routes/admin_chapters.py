from flask import Blueprint, request, jsonify, session
from datetime import datetime

from app import db
from app.models.book import Book
from app.models.chapter import Chapter


admin_chapters_bp = Blueprint(
    "admin_chapters",
    __name__,
    url_prefix="/api/admin/chapters"
)


# =========================================================
# ADMIN AUTH CHECK
# =========================================================

def admin_required():
    if not session.get("admin_id"):
        return jsonify({
            "success": False,
            "message": "Admin login required."
        }), 401

    return None


# =========================================================
# GET ALL CHAPTERS
# =========================================================

@admin_chapters_bp.route("", methods=["GET"])
def get_chapters():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    book_id = request.args.get("book_id", type=int)

    query = Chapter.query

    if book_id:
        query = query.filter_by(book_id=book_id)

    chapters = query.order_by(
        Chapter.chapter_number.asc()
    ).all()

    return jsonify({
        "success": True,
        "count": len(chapters),
        "chapters": [
            {
                "id": chapter.id,
                "book_id": chapter.book_id,
                "chapter_number": chapter.chapter_number,
                "title": chapter.title,
                "slug": chapter.slug,
                "content": chapter.content,
                "status": chapter.status,
                "publish_date": (
                    chapter.publish_date.isoformat()
                    if chapter.publish_date else None
                ),
                "created_at": (
                    chapter.created_at.isoformat()
                    if chapter.created_at else None
                ),
                "updated_at": (
                    chapter.updated_at.isoformat()
                    if chapter.updated_at else None
                )
            }
            for chapter in chapters
        ]
    })


# =========================================================
# GET SINGLE CHAPTER
# =========================================================

@admin_chapters_bp.route("/<int:chapter_id>", methods=["GET"])
def get_chapter(chapter_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    chapter = Chapter.query.get_or_404(chapter_id)

    return jsonify({
        "success": True,
        "chapter": {
            "id": chapter.id,
            "book_id": chapter.book_id,
            "chapter_number": chapter.chapter_number,
            "title": chapter.title,
            "slug": chapter.slug,
            "content": chapter.content,
            "status": chapter.status,
            "publish_date": (
                chapter.publish_date.isoformat()
                if chapter.publish_date else None
            )
        }
    })


# =========================================================
# CREATE CHAPTER
# =========================================================

@admin_chapters_bp.route("", methods=["POST"])
def create_chapter():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}

    book_id = data.get("book_id")
    chapter_number = data.get("chapter_number")
    title = data.get("title", "").strip()
    slug = data.get("slug", "").strip()

    if not book_id:
        return jsonify({
            "success": False,
            "message": "Book is required."
        }), 400

    if chapter_number is None:
        return jsonify({
            "success": False,
            "message": "Chapter number is required."
        }), 400

    if not title:
        return jsonify({
            "success": False,
            "message": "Chapter title is required."
        }), 400

    if not slug:
        return jsonify({
            "success": False,
            "message": "Chapter slug is required."
        }), 400

    book = Book.query.get(book_id)

    if not book:
        return jsonify({
            "success": False,
            "message": "Book not found."
        }), 404

    existing_slug = Chapter.query.filter_by(
        slug=slug
    ).first()

    if existing_slug:
        return jsonify({
            "success": False,
            "message": "Chapter slug already exists."
        }), 409

    existing_number = Chapter.query.filter_by(
        book_id=book_id,
        chapter_number=chapter_number
    ).first()

    if existing_number:
        return jsonify({
            "success": False,
            "message": "Chapter number already exists for this book."
        }), 409

    chapter = Chapter(
        book_id=book_id,
        chapter_number=chapter_number,
        title=title,
        slug=slug,
        content=data.get("content"),
        status=data.get("status", "draft")
    )

    publish_date = data.get("publish_date")

    if publish_date:
        try:
            chapter.publish_date = datetime.fromisoformat(
                publish_date
            )
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Invalid publish_date format."
            }), 400

    db.session.add(chapter)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Chapter created successfully.",
        "chapter_id": chapter.id
    }), 201


# =========================================================
# UPDATE CHAPTER
# =========================================================

@admin_chapters_bp.route("/<int:chapter_id>", methods=["PUT"])
def update_chapter(chapter_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    chapter = Chapter.query.get_or_404(chapter_id)

    data = request.get_json(silent=True) or {}

    if "book_id" in data:

        book = Book.query.get(data["book_id"])

        if not book:
            return jsonify({
                "success": False,
                "message": "Book not found."
            }), 404

        chapter.book_id = data["book_id"]

    if "chapter_number" in data:

        existing_number = Chapter.query.filter(
            Chapter.book_id == chapter.book_id,
            Chapter.chapter_number == data["chapter_number"],
            Chapter.id != chapter.id
        ).first()

        if existing_number:
            return jsonify({
                "success": False,
                "message": "Chapter number already exists for this book."
            }), 409

        chapter.chapter_number = data["chapter_number"]

    if "title" in data:

        title = str(data["title"]).strip()

        if not title:
            return jsonify({
                "success": False,
                "message": "Chapter title cannot be empty."
            }), 400

        chapter.title = title

    if "slug" in data:

        slug = str(data["slug"]).strip()

        if not slug:
            return jsonify({
                "success": False,
                "message": "Chapter slug cannot be empty."
            }), 400

        existing_slug = Chapter.query.filter(
            Chapter.slug == slug,
            Chapter.id != chapter.id
        ).first()

        if existing_slug:
            return jsonify({
                "success": False,
                "message": "Chapter slug already exists."
            }), 409

        chapter.slug = slug

    if "content" in data:
        chapter.content = data["content"]

    if "status" in data:
        chapter.status = data["status"]

    if "publish_date" in data:

        publish_date = data["publish_date"]

        if publish_date:
            try:
                chapter.publish_date = datetime.fromisoformat(
                    publish_date
                )
            except ValueError:
                return jsonify({
                    "success": False,
                    "message": "Invalid publish_date format."
                }), 400
        else:
            chapter.publish_date = None

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Chapter updated successfully.",
        "chapter_id": chapter.id
    })


# =========================================================
# DELETE CHAPTER
# =========================================================

@admin_chapters_bp.route("/<int:chapter_id>", methods=["DELETE"])
def delete_chapter(chapter_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    chapter = Chapter.query.get_or_404(chapter_id)

    db.session.delete(chapter)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Chapter deleted successfully."
    })


# =========================================================
# REORDER CHAPTERS
# =========================================================

@admin_chapters_bp.route("/reorder", methods=["POST"])
def reorder_chapters():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}

    chapters = data.get("chapters", [])

    if not isinstance(chapters, list):
        return jsonify({
            "success": False,
            "message": "Chapters must be a list."
        }), 400

    for item in chapters:

        chapter_id = item.get("id")
        position = item.get("chapter_number")

        if chapter_id is None or position is None:
            continue

        chapter = Chapter.query.get(chapter_id)

        if chapter:
            chapter.chapter_number = position

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Chapters reordered successfully."
    })
