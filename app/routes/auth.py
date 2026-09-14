# =========================================================
# RASBHAV BOOKS
# AUTHENTICATION API
# Flask + SQLite
# =========================================================

from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash

from app.models.admin import Admin


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


# =========================================================
# HELPERS
# =========================================================

def admin_to_dict(admin):
    """
    Convert Admin model into safe JSON data.
    Password hash is NEVER returned.
    """

    return {
        "id": admin.id,
        "username": admin.username,
        "full_name": admin.full_name,
        "is_super_admin": bool(admin.is_super_admin),
        "is_active": bool(admin.is_active)
    }


def get_current_admin():
    """
    Return currently logged-in admin.
    """

    admin_id = session.get("admin_id")

    if not admin_id:
        return None

    admin = Admin.query.get(admin_id)

    if not admin or not admin.is_active:
        session.pop("admin_id", None)
        session.pop("admin_logged_in", None)
        return None

    return admin


# =========================================================
# LOGIN
# =========================================================

@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    username = str(
        data.get("username", "")
    ).strip()

    password = data.get("password", "")

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not username or not password:

        return jsonify({
            "success": False,
            "message": "Username and password are required."
        }), 400

    # -----------------------------------------------------
    # FIND ADMIN
    # -----------------------------------------------------

    admin = Admin.query.filter_by(
        username=username
    ).first()

    # -----------------------------------------------------
    # CHECK ACCOUNT
    # -----------------------------------------------------

    if not admin:

        return jsonify({
            "success": False,
            "message": "Invalid username or password."
        }), 401

    if not admin.is_active:

        return jsonify({
            "success": False,
            "message": "This admin account is inactive."
        }), 403

    # -----------------------------------------------------
    # CHECK PASSWORD
    # -----------------------------------------------------

    if not admin.password_hash:

        return jsonify({
            "success": False,
            "message": "Admin account password is not configured."
        }), 500

    if not check_password_hash(
        admin.password_hash,
        password
    ):

        return jsonify({
            "success": False,
            "message": "Invalid username or password."
        }), 401

    # -----------------------------------------------------
    # CREATE SESSION
    # -----------------------------------------------------

    session.clear()

    session["admin_id"] = admin.id
    session["admin_logged_in"] = True

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "admin": admin_to_dict(admin)
    }), 200


# =========================================================
# LOGOUT
# =========================================================

@auth_bp.route("/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "success": True,
        "message": "Logout successful."
    }), 200


# =========================================================
# AUTH STATUS
# =========================================================

@auth_bp.route("/status", methods=["GET"])
def status():

    admin = get_current_admin()

    if not admin:

        return jsonify({
            "success": True,
            "authenticated": False,
            "admin": None
        }), 200

    return jsonify({
        "success": True,
        "authenticated": True,
        "admin": admin_to_dict(admin)
    }), 200


# =========================================================
# CURRENT ADMIN
# =========================================================

@auth_bp.route("/me", methods=["GET"])
def me():

    admin = get_current_admin()

    if not admin:

        return jsonify({
            "success": False,
            "authenticated": False,
            "message": "Authentication required."
        }), 401

    return jsonify({
        "success": True,
        "authenticated": True,
        "admin": admin_to_dict(admin)
    }), 200
