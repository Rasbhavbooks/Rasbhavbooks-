from flask import Blueprint, request, jsonify, session

from app import db
from app.models.media import Media


admin_media_bp = Blueprint(
    "admin_media",
    __name__,
    url_prefix="/api/admin/media"
)


def admin_required():
    if not session.get("admin_id"):
        return jsonify({
            "success": False,
            "message": "Admin login required."
        }), 401

    return None


# =========================================================
# GET ALL MEDIA
# =========================================================

@admin_media_bp.route("", methods=["GET"])
def get_media():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    media_items = Media.query.order_by(
        Media.created_at.desc()
    ).all()

    return jsonify({
        "success": True,
        "count": len(media_items),
        "media": [
            {
                "id": item.id,
                "name": item.name,
                "file_name": item.file_name,
                "file_path": item.file_path,
                "file_type": item.file_type,
                "mime_type": item.mime_type,
                "alt_text": item.alt_text,
                "title": item.title,
                "description": item.description,
                "url": item.url,
                "created_at": (
                    item.created_at.isoformat()
                    if item.created_at else None
                )
            }
            for item in media_items
        ]
    })


# =========================================================
# GET SINGLE MEDIA
# =========================================================

@admin_media_bp.route("/<int:media_id>", methods=["GET"])
def get_single_media(media_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    item = Media.query.get_or_404(media_id)

    return jsonify({
        "success": True,
        "media": {
            "id": item.id,
            "name": item.name,
            "file_name": item.file_name,
            "file_path": item.file_path,
            "file_type": item.file_type,
            "mime_type": item.mime_type,
            "alt_text": item.alt_text,
            "title": item.title,
            "description": item.description,
            "url": item.url
        }
    })


# =========================================================
# CREATE MEDIA RECORD
# =========================================================

@admin_media_bp.route("", methods=["POST"])
def create_media():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}

    name = str(
        data.get("name", "")
    ).strip()

    file_name = str(
        data.get("file_name", "")
    ).strip()

    file_path = str(
        data.get("file_path", "")
    ).strip()

    if not name:
        return jsonify({
            "success": False,
            "message": "Media name is required."
        }), 400

    if not file_path:
        return jsonify({
            "success": False,
            "message": "File path is required."
        }), 400

    item = Media(
        name=name,
        file_name=file_name,
        file_path=file_path,
        file_type=data.get("file_type"),
        mime_type=data.get("mime_type"),
        alt_text=data.get("alt_text"),
        title=data.get("title"),
        description=data.get("description"),
        url=data.get("url")
    )

    db.session.add(item)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Media created successfully.",
        "media_id": item.id
    }), 201


# =========================================================
# UPDATE MEDIA
# =========================================================

@admin_media_bp.route("/<int:media_id>", methods=["PUT"])
def update_media(media_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    item = Media.query.get_or_404(media_id)

    data = request.get_json(silent=True) or {}

    if "name" in data:
        item.name = str(
            data["name"]
        ).strip()

    if "file_name" in data:
        item.file_name = data["file_name"]

    if "file_path" in data:
        item.file_path = data["file_path"]

    if "file_type" in data:
        item.file_type = data["file_type"]

    if "mime_type" in data:
        item.mime_type = data["mime_type"]

    if "alt_text" in data:
        item.alt_text = data["alt_text"]

    if "title" in data:
        item.title = data["title"]

    if "description" in data:
        item.description = data["description"]

    if "url" in data:
        item.url = data["url"]

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Media updated successfully.",
        "media_id": item.id
    })


# =========================================================
# DELETE MEDIA
# =========================================================

@admin_media_bp.route("/<int:media_id>", methods=["DELETE"])
def delete_media(media_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    item = Media.query.get_or_404(media_id)

    db.session.delete(item)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Media deleted successfully."
    })
