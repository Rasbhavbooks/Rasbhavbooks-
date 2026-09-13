from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash

from app.models.admin import Admin


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({
            "success": False,
            "message": "Username and password are required."
        }), 400

    admin = Admin.query.filter_by(
        username=username,
        is_active=True
    ).first()

    if not admin or not check_password_hash(
        admin.password_hash,
        password
    ):
        return jsonify({
            "success": False,
            "message": "Invalid username or password."
        }), 401

    session["admin_id"] = admin.id
    session["admin_logged_in"] = True

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "admin": {
            "id": admin.id,
            "username": admin.username,
            "full_name": admin.full_name,
            "is_super_admin": admin.is_super_admin
        }
    })


@auth_bp.route("/logout", methods=["POST"])
def logout():

    session.pop("admin_id", None)
    session.pop("admin_logged_in", None)

    return jsonify({
        "success": True,
        "message": "Logout successful."
    })


@auth_bp.route("/status", methods=["GET"])
def status():

    admin_id = session.get("admin_id")

    if not admin_id:
        return jsonify({
            "authenticated": False
        })

    admin = Admin.query.get(admin_id)

    if not admin or not admin.is_active:
        session.clear()

        return jsonify({
            "authenticated": False
        })

    return jsonify({
        "authenticated": True,
        "admin": {
            "id": admin.id,
            "username": admin.username,
            "full_name": admin.full_name,
            "is_super_admin": admin.is_super_admin
        }
    })
