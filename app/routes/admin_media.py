# ============================================================
# RASBHAV BOOKS
# ADMIN MEDIA ROUTES / API
# ============================================================
#
# ADMIN PANEL
#      ↓
# MEDIA MANAGEMENT API
#      ↓
# MEDIA DATABASE
#      ↓
# PUBLIC WEBSITE
#
# Supports:
# - Media library
# - Images
# - Documents
# - File metadata
# - URL
# - Alt text
# - Title
# - Caption
# - Description
# - File size
# - Dimensions
# - MIME type
# - Uploaded by admin
# - Search
# - File type filter
# - Image filter
# - Pagination / limit
# - CRUD
# ============================================================


from flask import (
    Blueprint,
    request,
    jsonify,
)

from app import db

from app.models.media import Media
from app.models.admin import Admin

from app.routes.admin import admin_required


# ============================================================
# BLUEPRINT
# ============================================================

admin_media_bp = Blueprint(
    "admin_media",
    __name__,
    url_prefix="/api/admin/media"
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


# ============================================================
# MEDIA SERIALIZER
# ============================================================

def media_to_dict(
    item,
    include_uploader=True
):

    data = {

        "id":
            item.id,

        "filename":
            item.get_filename(),

        "file_name":
            item.get_filename(),

        "file_path":
            item.get_file_path(),

        "file_type":
            item.get_file_type(),

        "mime_type":
            item.get_mime_type(),

        "file_size":
            item.file_size,

        "file_size_kb":
            item.get_file_size_kb(),

        "file_size_mb":
            item.get_file_size_mb(),

        "url":
            item.get_url(),

        "alt_text":
            item.alt_text,

        "title":
            item.title,

        "caption":
            item.caption,

        "description":
            item.description,

        "width":
            item.width,

        "height":
            item.height,

        "dimensions":
            item.get_dimensions(),

        "is_image":
            item.is_image(),

        "has_dimensions":
            item.has_dimensions(),

        "created_at": (
            item.created_at.isoformat()
            if item.created_at
            else None
        ),

        "updated_at": (
            item.updated_at.isoformat()
            if item.updated_at
            else None
        ),

        "uploaded_by":
            item.uploaded_by
    }

    # --------------------------------------------------------
    # UPLOADER
    # --------------------------------------------------------

    if include_uploader:

        uploader = item.uploader

        if uploader:

            data["uploader"] = {

                "id":
                    uploader.id,

                "username":
                    uploader.username,

                "full_name":
                    uploader.full_name
            }

        else:

            data["uploader"] = None

    return data


# ============================================================
# GET ALL MEDIA
# ============================================================

@admin_media_bp.route(
    "",
    methods=["GET"]
)
@admin_media_bp.route(
    "/",
    methods=["GET"]
)
def get_media():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        query = Media.query

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
                    Media.filename.ilike(
                        pattern
                    ),

                    Media.title.ilike(
                        pattern
                    ),

                    Media.alt_text.ilike(
                        pattern
                    ),

                    Media.caption.ilike(
                        pattern
                    ),

                    Media.description.ilike(
                        pattern
                    ),

                    Media.file_type.ilike(
                        pattern
                    ),

                    Media.mime_type.ilike(
                        pattern
                    )
                )
            )

        # ----------------------------------------------------
        # FILE TYPE FILTER
        # ----------------------------------------------------

        file_type = clean_string(
            request.args.get(
                "file_type"
            )
        )

        if file_type:

            query = query.filter(
                Media.file_type.ilike(
                    file_type
                )
            )

        # ----------------------------------------------------
        # MIME TYPE FILTER
        # ----------------------------------------------------

        mime_type = clean_string(
            request.args.get(
                "mime_type"
            )
        )

        if mime_type:

            query = query.filter(
                Media.mime_type.ilike(
                    mime_type
                )
            )

        # ----------------------------------------------------
        # IMAGE FILTER
        # ----------------------------------------------------

        image_only = (
            request.args.get(
                "image_only"
            )
        )

        if image_only:

            image_only = (
                str(
                    image_only
                )
                .strip()
                .lower()
            )

            if image_only in (
                "1",
                "true",
                "yes",
                "on"
            ):

                query = query.filter(
                    Media.mime_type.ilike(
                        "image/%"
                    )
                )

        # ----------------------------------------------------
        # UPLOADER FILTER
        # ----------------------------------------------------

        if "uploaded_by" in request.args:

            uploaded_by = parse_int(
                request.args.get(
                    "uploaded_by"
                )
            )

            if uploaded_by is None:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Invalid uploaded_by."

                }), 400

            query = query.filter(
                Media.uploaded_by
                == uploaded_by
            )

        # ----------------------------------------------------
        # LIMIT
        # ----------------------------------------------------

        limit = request.args.get(
            "limit",
            50,
            type=int
        )

        if limit < 1:
            limit = 1

        if limit > 200:
            limit = 200

        # ----------------------------------------------------
        # FETCH
        # ----------------------------------------------------

        media_items = (
            query
            .order_by(
                Media.created_at.desc(),
                Media.id.desc()
            )
            .limit(limit)
            .all()
        )

        return jsonify({

            "success":
                True,

            "count":
                len(media_items),

            "media":
                [
                    media_to_dict(
                        item
                    )
                    for item in media_items
                ]

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load media library.",

            "error":
                str(error)

        }), 500


# ============================================================
# GET SINGLE MEDIA
# ============================================================

@admin_media_bp.route(
    "/<int:media_id>",
    methods=["GET"]
)
def get_single_media(media_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        item = Media.query.get(
            media_id
        )

        if not item:

            return jsonify({

                "success":
                    False,

                "message":
                    "Media not found."

            }), 404

        return jsonify({

            "success":
                True,

            "media":
                media_to_dict(
                    item
                )

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load media.",

            "error":
                str(error)

        }), 500


# ============================================================
# CREATE MEDIA RECORD
# ============================================================

@admin_media_bp.route(
    "",
    methods=["POST"]
)
@admin_media_bp.route(
    "/",
    methods=["POST"]
)
def create_media():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(
        silent=True
    ) or {}

    try:

        # ----------------------------------------------------
        # REQUIRED FIELDS
        # ----------------------------------------------------

        filename = clean_string(
            data.get(
                "filename",
                data.get(
                    "file_name"
                )
            )
        )

        file_path = clean_string(
            data.get(
                "file_path"
            )
        )

        if not filename:

            return jsonify({

                "success":
                    False,

                "message":
                    "Filename is required."

            }), 400

        if not file_path:

            return jsonify({

                "success":
                    False,

                "message":
                    "File path is required."

            }), 400

        # ----------------------------------------------------
        # ADMIN
        # ----------------------------------------------------

        from flask import session

        uploaded_by = session.get(
            "admin_id"
        )

        if uploaded_by:

            uploaded_by = parse_int(
                uploaded_by
            )

            if uploaded_by:

                admin = Admin.query.get(
                    uploaded_by
                )

                if not admin:

                    uploaded_by = None

        # ----------------------------------------------------
        # FILE SIZE
        # ----------------------------------------------------

        file_size = parse_int(
            data.get(
                "file_size"
            )
        )

        if file_size is not None and file_size < 0:

            return jsonify({

                "success":
                    False,

                "message":
                    "File size cannot be negative."

            }), 400

        # ----------------------------------------------------
        # DIMENSIONS
        # ----------------------------------------------------

        width = parse_int(
            data.get(
                "width"
            )
        )

        height = parse_int(
            data.get(
                "height"
            )
        )

        if width is not None and width < 0:

            return jsonify({

                "success":
                    False,

                "message":
                    "Width cannot be negative."

            }), 400

        if height is not None and height < 0:

            return jsonify({

                "success":
                    False,

                "message":
                    "Height cannot be negative."

            }), 400

        # ----------------------------------------------------
        # CREATE
        # ----------------------------------------------------

        item = Media(

            filename=filename,

            file_path=file_path,

            file_type=clean_string(
                data.get(
                    "file_type"
                )
            ),

            mime_type=clean_string(
                data.get(
                    "mime_type"
                )
            ),

            file_size=file_size,

            url=clean_string(
                data.get(
                    "url"
                )
            ),

            alt_text=clean_string(
                data.get(
                    "alt_text"
                )
            ),

            title=clean_string(
                data.get(
                    "title"
                )
            ),

            caption=clean_string(
                data.get(
                    "caption"
                )
            ),

            description=clean_string(
                data.get(
                    "description"
                )
            ),

            width=width,

            height=height,

            uploaded_by=uploaded_by
        )

        db.session.add(
            item
        )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Media created successfully.",

            "media":
                media_to_dict(
                    item
                )

        }), 201

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to create media.",

            "error":
                str(error)

        }), 500


# ============================================================
# UPDATE MEDIA
# ============================================================

@admin_media_bp.route(
    "/<int:media_id>",
    methods=["PUT", "PATCH"]
)
def update_media(media_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(
        silent=True
    ) or {}

    try:

        item = Media.query.get(
            media_id
        )

        if not item:

            return jsonify({

                "success":
                    False,

                "message":
                    "Media not found."

            }), 404

        # ----------------------------------------------------
        # FILENAME
        # ----------------------------------------------------

        if (
            "filename" in data
            or "file_name" in data
        ):

            filename = clean_string(
                data.get(
                    "filename",
                    data.get(
                        "file_name"
                    )
                )
            )

            if not filename:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Filename cannot be empty."

                }), 400

            item.filename = filename

        # ----------------------------------------------------
        # FILE PATH
        # ----------------------------------------------------

        if "file_path" in data:

            file_path = clean_string(
                data.get(
                    "file_path"
                )
            )

            if not file_path:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "File path cannot be empty."

                }), 400

            item.file_path = file_path

        # ----------------------------------------------------
        # FILE TYPE
        # ----------------------------------------------------

        if "file_type" in data:

            item.file_type = clean_string(
                data.get(
                    "file_type"
                )
            )

        # ----------------------------------------------------
        # MIME TYPE
        # ----------------------------------------------------

        if "mime_type" in data:

            item.mime_type = clean_string(
                data.get(
                    "mime_type"
                )
            )

        # ----------------------------------------------------
        # FILE SIZE
        # ----------------------------------------------------

        if "file_size" in data:

            file_size = parse_int(
                data.get(
                    "file_size"
                )
            )

            if (
                file_size is not None
                and file_size < 0
            ):

                return jsonify({

                    "success":
                        False,

                    "message":
                        "File size cannot be negative."

                }), 400

            item.file_size = file_size

        # ----------------------------------------------------
        # URL
        # ----------------------------------------------------

        if "url" in data:

            item.url = clean_string(
                data.get(
                    "url"
                )
            )

        # ----------------------------------------------------
        # ALT TEXT
        # ----------------------------------------------------

        if "alt_text" in data:

            item.alt_text = clean_string(
                data.get(
                    "alt_text"
                )
            )

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        if "title" in data:

            item.title = clean_string(
                data.get(
                    "title"
                )
            )

        # ----------------------------------------------------
        # CAPTION
        # ----------------------------------------------------

        if "caption" in data:

            item.caption = clean_string(
                data.get(
                    "caption"
                )
            )

        # ----------------------------------------------------
        # DESCRIPTION
        # ----------------------------------------------------

        if "description" in data:

            item.description = clean_string(
                data.get(
                    "description"
                )
            )

        # ----------------------------------------------------
        # WIDTH
        # ----------------------------------------------------

        if "width" in data:

            width = parse_int(
                data.get(
                    "width"
                )
            )

            if (
                width is not None
                and width < 0
            ):

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Width cannot be negative."

                }), 400

            item.width = width

        # ----------------------------------------------------
        # HEIGHT
        # ----------------------------------------------------

        if "height" in data:

            height = parse_int(
                data.get(
                    "height"
                )
            )

            if (
                height is not None
                and height < 0
            ):

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Height cannot be negative."

                }), 400

            item.height = height

        # ----------------------------------------------------
        # UPLOADED BY
        # ----------------------------------------------------

        if "uploaded_by" in data:

            uploaded_by = parse_int(
                data.get(
                    "uploaded_by"
                )
            )

            if uploaded_by is not None:

                admin = Admin.query.get(
                    uploaded_by
                )

                if not admin:

                    return jsonify({

                        "success":
                            False,

                        "message":
                            "Uploader admin not found."

                    }), 404

            item.uploaded_by = uploaded_by

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Media updated successfully.",

            "media":
                media_to_dict(
                    item
                )

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to update media.",

            "error":
                str(error)

        }), 500


# ============================================================
# DELETE MEDIA
# ============================================================

@admin_media_bp.route(
    "/<int:media_id>",
    methods=["DELETE"]
)
def delete_media(media_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        item = Media.query.get(
            media_id
        )

        if not item:

            return jsonify({

                "success":
                    False,

                "message":
                    "Media not found."

            }), 404

        deleted_id = item.id

        db.session.delete(
            item
        )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Media deleted successfully.",

            "media_id":
                deleted_id

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to delete media.",

            "error":
                str(error)

        }), 500


# ============================================================
# MEDIA STATS
# ============================================================

@admin_media_bp.route(
    "/stats",
    methods=["GET"]
)
def media_stats():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        total = Media.query.count()

        images = (
            Media.query
            .filter(
                Media.mime_type.ilike(
                    "image/%"
                )
            )
            .count()
        )

        videos = (
            Media.query
            .filter(
                Media.mime_type.ilike(
                    "video/%"
                )
            )
            .count()
        )

        documents = (
            Media.query
            .filter(
                Media.mime_type.ilike(
                    "application/%"
                )
            )
            .count()
        )

        total_size = db.session.query(
            db.func.coalesce(
                db.func.sum(
                    Media.file_size
                ),
                0
            )
        ).scalar()

        return jsonify({

            "success":
                True,

            "stats": {

                "total":
                    total,

                "images":
                    images,

                "videos":
                    videos,

                "documents":
                    documents,

                "total_size":
                    int(
                        total_size or 0
                    ),

                "total_size_mb":
                    round(
                        (
                            int(
                                total_size or 0
                            )
                            /
                            (
                                1024 * 1024
                            )
                        ),
                        2
                    )
            }

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load media statistics.",

            "error":
                str(error)

        }), 500
