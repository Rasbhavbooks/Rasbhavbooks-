from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash

from app import db
from app.models.user import User


admin_users_bp = Blueprint(
    "admin_users",
    __name__,
    url_prefix="/api/admin/users"
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
# GET ALL USERS
# =========================================================

@admin_users_bp.route("", methods=["GET"])
def get_users():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    users = User.query.order_by(
        User.created_at.desc()
    ).all()

    return jsonify({
        "success": True,
        "count": len(users),
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "created_at": (
                    user.created_at.isoformat()
                    if user.created_at else None
                ),
                "updated_at": (
                    user.updated_at.isoformat()
                    if user.updated_at else None
                )
            }
            for user in users
        ]
    })


# =========================================================
# GET SINGLE USER
# =========================================================

@admin_users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    user = User.query.get_or_404(user_id)

    return jsonify({
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "created_at": (
                user.created_at.isoformat()
                if user.created_at else None
            ),
            "updated_at": (
                user.updated_at.isoformat()
                if user.updated_at else None
            )
        }
    })


# =========================================================
# UPDATE USER
# =========================================================

@admin_users_bp.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    user = User.query.get_or_404(user_id)

    data = request.get_json(silent=True) or {}

    if "username" in data:

        username = str(data["username"]).strip()

        if not username:
            return jsonify({
                "success": False,
                "message": "Username cannot be empty."
            }), 400

        existing = User.query.filter(
            User.username == username,
            User.id != user.id
        ).first()

        if existing:
            return jsonify({
                "success": False,
                "message": "Username already exists."
            }), 409

        user.username = username

    if "email" in data:

        email = str(data["email"]).strip().lower()

        if not email:
            return jsonify({
                "success": False,
                "message": "Email cannot be empty."
            }), 400

        existing = User.query.filter(
            User.email == email,
            User.id != user.id
        ).first()

        if existing:
            return jsonify({
                "success": False,
                "message": "Email already exists."
            }), 409

        user.email = email

    if "full_name" in data:
        user.full_name = data["full_name"]

    if "is_active" in data:
        user.is_active = bool(data["is_active"])

    if "password" in data:

        password = str(data["password"])

        if password:

            if len(password) < 6:
                return jsonify({
                    "success": False,
                    "message": "Password must be at least 6 characters."
                }), 400

            user.password_hash = generate_password_hash(
                password
            )

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "User updated successfully.",
        "user_id": user.id
    })


# =========================================================
# ACTIVATE / DEACTIVATE USER
# =========================================================

@admin_users_bp.route("/<int:user_id>/status", methods=["PATCH"])
def update_user_status(user_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    user = User.query.get_or_404(user_id)

    data = request.get_json(silent=True) or {}

    if "is_active" not in data:
        return jsonify({
            "success": False,
            "message": "is_active is required."
        }), 400

    user.is_active = bool(data["is_active"])

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "User status updated successfully.",
        "user_id": user.id,
        "is_active": user.is_active
    })


# =========================================================
# DELETE USER
# =========================================================

@admin_users_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "User deleted successfully."
    })
