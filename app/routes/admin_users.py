# ============================================================
# RASBHAV BOOKS
# ADMIN USERS ROUTES / API
# ============================================================
#
# ADMIN PANEL
#      ↓
# USER MANAGEMENT API
#      ↓
# DATABASE
#
# Features:
# - Admin authentication
# - User listing
# - Search
# - Pagination / limit
# - Single user details
# - Create user
# - Update user
# - Password management
# - Activate / deactivate
# - User statistics
# - Safe delete
# - Validation
# - Rollback on errors
# ============================================================


from flask import Blueprint, request, jsonify

from app import db

from app.models.user import User
from app.models.favorite import Favorite
from app.models.bookmark import Bookmark
from app.models.reading_progress import ReadingProgress

from app.routes.admin import admin_required


# ============================================================
# BLUEPRINT
# ============================================================

admin_users_bp = Blueprint(
    "admin_users",
    __name__,
    url_prefix="/api/admin/users"
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


def parse_bool(value, default=None):

    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, int):

        if value == 1:
            return True

        if value == 0:
            return False

    if isinstance(value, str):

        value = value.strip().lower()

        if value in (
            "true",
            "1",
            "yes",
            "on",
            "active",
            "enabled"
        ):
            return True

        if value in (
            "false",
            "0",
            "no",
            "off",
            "inactive",
            "disabled"
        ):
            return False

    return default


# ============================================================
# USER SERIALIZER
# ============================================================

def user_to_dict(
    user,
    include_stats=False
):

    data = {

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
        ),

        "updated_at": (
            user.updated_at.isoformat()
            if user.updated_at
            else None
        )
    }

    # --------------------------------------------------------
    # OPTIONAL STATISTICS
    # --------------------------------------------------------

    if include_stats:

        data["stats"] = {

            "favorites":
                Favorite.query
                .filter_by(
                    user_id=user.id
                )
                .count(),

            "bookmarks":
                Bookmark.query
                .filter_by(
                    user_id=user.id
                )
                .count(),

            "reading_progress":
                ReadingProgress.query
                .filter_by(
                    user_id=user.id
                )
                .count()
        }

    return data


# ============================================================
# GET ALL USERS
# ============================================================

@admin_users_bp.route(
    "",
    methods=["GET"]
)
@admin_users_bp.route(
    "/",
    methods=["GET"]
)
def get_users():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        query = User.query

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
                    User.username.ilike(
                        pattern
                    ),

                    User.email.ilike(
                        pattern
                    ),

                    User.full_name.ilike(
                        pattern
                    )
                )
            )

        # ----------------------------------------------------
        # ACTIVE FILTER
        # ----------------------------------------------------

        if "is_active" in request.args:

            active = parse_bool(
                request.args.get(
                    "is_active"
                )
            )

            if active is None:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Invalid is_active value."

                }), 400

            query = query.filter(
                User.is_active == active
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

            limit = 100

        if limit < 1:
            limit = 1

        if limit > 500:
            limit = 500

        # ----------------------------------------------------
        # FETCH
        # ----------------------------------------------------

        users = (
            query
            .order_by(
                User.created_at.desc()
            )
            .limit(limit)
            .all()
        )

        return jsonify({

            "success":
                True,

            "count":
                len(users),

            "users": [

                user_to_dict(
                    user
                )

                for user in users
            ]

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load users.",

            "error":
                str(error)

        }), 500


# ============================================================
# GET SINGLE USER
# ============================================================

@admin_users_bp.route(
    "/<int:user_id>",
    methods=["GET"]
)
def get_user(user_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        user = User.query.get(
            user_id
        )

        if not user:

            return jsonify({

                "success":
                    False,

                "message":
                    "User not found."

            }), 404

        return jsonify({

            "success":
                True,

            "user":
                user_to_dict(
                    user,
                    include_stats=True
                )

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load user.",

            "error":
                str(error)

        }), 500


# ============================================================
# CREATE USER
# ============================================================

@admin_users_bp.route(
    "",
    methods=["POST"]
)
@admin_users_bp.route(
    "/",
    methods=["POST"]
)
def create_user():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(
        silent=True
    ) or {}

    try:

        # ----------------------------------------------------
        # USERNAME
        # ----------------------------------------------------

        username = clean_string(
            data.get(
                "username"
            )
        )

        if not username:

            return jsonify({

                "success":
                    False,

                "message":
                    "Username is required."

            }), 400

        # ----------------------------------------------------
        # EMAIL
        # ----------------------------------------------------

        email = clean_string(
            data.get(
                "email"
            )
        )

        if not email:

            return jsonify({

                "success":
                    False,

                "message":
                    "Email is required."

            }), 400

        email = email.lower()

        # ----------------------------------------------------
        # PASSWORD
        # ----------------------------------------------------

        password = data.get(
            "password"
        )

        if password is None:

            return jsonify({

                "success":
                    False,

                "message":
                    "Password is required."

            }), 400

        password = str(
            password
        )

        if len(password) < 6:

            return jsonify({

                "success":
                    False,

                "message":
                    "Password must be at least 6 characters."

            }), 400

        # ----------------------------------------------------
        # USERNAME UNIQUE
        # ----------------------------------------------------

        existing_username = (
            User.query
            .filter_by(
                username=username
            )
            .first()
        )

        if existing_username:

            return jsonify({

                "success":
                    False,

                "message":
                    "Username already exists."

            }), 409

        # ----------------------------------------------------
        # EMAIL UNIQUE
        # ----------------------------------------------------

        existing_email = (
            User.query
            .filter_by(
                email=email
            )
            .first()
        )

        if existing_email:

            return jsonify({

                "success":
                    False,

                "message":
                    "Email already exists."

            }), 409

        # ----------------------------------------------------
        # ACTIVE STATUS
        # ----------------------------------------------------

        is_active = parse_bool(
            data.get(
                "is_active"
            ),
            True
        )

        # ----------------------------------------------------
        # CREATE
        # ----------------------------------------------------

        user = User(

            username=username,

            email=email,

            full_name=clean_string(
                data.get(
                    "full_name"
                )
            ),

            is_active=is_active
        )

        user.set_password(
            password
        )

        db.session.add(
            user
        )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "User created successfully.",

            "user":
                user_to_dict(
                    user,
                    include_stats=True
                )

        }), 201

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to create user.",

            "error":
                str(error)

        }), 500


# ============================================================
# UPDATE USER
# ============================================================

@admin_users_bp.route(
    "/<int:user_id>",
    methods=["PUT", "PATCH"]
)
def update_user(user_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(
        silent=True
    ) or {}

    try:

        user = User.query.get(
            user_id
        )

        if not user:

            return jsonify({

                "success":
                    False,

                "message":
                    "User not found."

            }), 404

        # ----------------------------------------------------
        # USERNAME
        # ----------------------------------------------------

        if "username" in data:

            username = clean_string(
                data.get(
                    "username"
                )
            )

            if not username:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Username cannot be empty."

                }), 400

            existing = (
                User.query
                .filter(
                    User.username == username,
                    User.id != user.id
                )
                .first()
            )

            if existing:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Username already exists."

                }), 409

            user.username = username

        # ----------------------------------------------------
        # EMAIL
        # ----------------------------------------------------

        if "email" in data:

            email = clean_string(
                data.get(
                    "email"
                )
            )

            if not email:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Email cannot be empty."

                }), 400

            email = email.lower()

            existing = (
                User.query
                .filter(
                    User.email == email,
                    User.id != user.id
                )
                .first()
            )

            if existing:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Email already exists."

                }), 409

            user.email = email

        # ----------------------------------------------------
        # FULL NAME
        # ----------------------------------------------------

        if "full_name" in data:

            user.full_name = clean_string(
                data.get(
                    "full_name"
                )
            )

        # ----------------------------------------------------
        # ACTIVE STATUS
        # ----------------------------------------------------

        if "is_active" in data:

            is_active = parse_bool(
                data.get(
                    "is_active"
                )
            )

            if is_active is None:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Invalid is_active value."

                }), 400

            user.is_active = is_active

        # ----------------------------------------------------
        # PASSWORD
        # ----------------------------------------------------

        if "password" in data:

            password = data.get(
                "password"
            )

            if password:

                password = str(
                    password
                )

                if len(password) < 6:

                    return jsonify({

                        "success":
                            False,

                        "message":
                            "Password must be at least 6 characters."

                    }), 400

                user.set_password(
                    password
                )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "User updated successfully.",

            "user":
                user_to_dict(
                    user,
                    include_stats=True
                )

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to update user.",

            "error":
                str(error)

        }), 500


# ============================================================
# ACTIVATE / DEACTIVATE USER
# ============================================================

@admin_users_bp.route(
    "/<int:user_id>/status",
    methods=["PATCH"]
)
def update_user_status(user_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(
        silent=True
    ) or {}

    try:

        user = User.query.get(
            user_id
        )

        if not user:

            return jsonify({

                "success":
                    False,

                "message":
                    "User not found."

            }), 404

        if "is_active" not in data:

            return jsonify({

                "success":
                    False,

                "message":
                    "is_active is required."

            }), 400

        is_active = parse_bool(
            data.get(
                "is_active"
            )
        )

        if is_active is None:

            return jsonify({

                "success":
                    False,

                "message":
                    "Invalid is_active value."

            }), 400

        user.is_active = is_active

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "User status updated successfully.",

            "user":
                user_to_dict(
                    user
                )

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to update user status.",

            "error":
                str(error)

        }), 500


# ============================================================
# DELETE USER
# ============================================================

@admin_users_bp.route(
    "/<int:user_id>",
    methods=["DELETE"]
)
def delete_user(user_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        user = User.query.get(
            user_id
        )

        if not user:

            return jsonify({

                "success":
                    False,

                "message":
                    "User not found."

            }), 404

        # ----------------------------------------------------
        # DELETE USER DATA FIRST
        # ----------------------------------------------------

        Favorite.query.filter_by(
            user_id=user.id
        ).delete(
            synchronize_session=False
        )

        Bookmark.query.filter_by(
            user_id=user.id
        ).delete(
            synchronize_session=False
        )

        ReadingProgress.query.filter_by(
            user_id=user.id
        ).delete(
            synchronize_session=False
        )

        # ----------------------------------------------------
        # DELETE USER
        # ----------------------------------------------------

        db.session.delete(
            user
        )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "User deleted successfully.",

            "user_id":
                user_id

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to delete user.",

            "error":
                str(error)

        }), 500


# ============================================================
# USER STATISTICS
# ============================================================

@admin_users_bp.route(
    "/stats",
    methods=["GET"]
)
def user_stats():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        total_users = User.query.count()

        active_users = (
            User.query
            .filter(
                User.is_active.is_(True)
            )
            .count()
        )

        inactive_users = (
            User.query
            .filter(
                User.is_active.is_(False)
            )
            .count()
        )

        total_favorites = (
            Favorite.query.count()
        )

        total_bookmarks = (
            Bookmark.query.count()
        )

        total_reading_progress = (
            ReadingProgress.query.count()
        )

        return jsonify({

            "success":
                True,

            "stats": {

                "total_users":
                    total_users,

                "active_users":
                    active_users,

                "inactive_users":
                    inactive_users,

                "total_favorites":
                    total_favorites,

                "total_bookmarks":
                    total_bookmarks,

                "total_reading_progress":
                    total_reading_progress
            }

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load user statistics.",

            "error":
                str(error)

        }), 500
