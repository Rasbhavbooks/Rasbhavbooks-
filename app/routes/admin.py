# =========================================================
# RASBHAV BOOKS
# ADMIN CORE ROUTES
# =========================================================

from functools import wraps

from flask import (
    Blueprint,
    render_template,
    jsonify,
    session,
    redirect,
    url_for,
)

from app.models.admin import Admin


# =========================================================
# BLUEPRINT
# =========================================================

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/api/admin"
)


# =========================================================
# CURRENT ADMIN
# =========================================================

def get_current_admin():
    """
    Return the currently authenticated Admin.

    Uses admin_id stored in the Flask session.
    Invalid or inactive admins are automatically logged out.
    """

    admin_id = session.get("admin_id")

    if not admin_id:
        return None

    try:
        admin = Admin.query.get(admin_id)
    except Exception:
        return None

    if not admin or not admin.is_active:
        session.pop("admin_id", None)
        session.pop("admin_logged_in", None)
        return None

    return admin


# =========================================================
# AUTH CHECK
# =========================================================

def is_admin_logged_in():
    return get_current_admin() is not None


def admin_required():
    """
    API authentication helper.

    Returns:
        None       -> authenticated
        JSON 401   -> not authenticated
    """

    admin = get_current_admin()

    if not admin:
        return jsonify({
            "success": False,
            "authenticated": False,
            "message": "Admin login required."
        }), 401

    return None


# =========================================================
# ADMIN DECORATOR
# =========================================================

def require_admin(view_function):
    """
    Decorator for protected Admin API routes.

    Usage:

        @some_bp.route("/something")
        @require_admin
        def something():
            ...
    """

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        admin = get_current_admin()

        if not admin:
            return jsonify({
                "success": False,
                "authenticated": False,
                "message": "Admin login required."
            }), 401

        return view_function(
            *args,
            **kwargs
        )

    return wrapped_view


# =========================================================
# SUPER ADMIN CHECK
# =========================================================

def is_super_admin():
    admin = get_current_admin()

    if not admin:
        return False

    return bool(admin.is_super_admin)


def super_admin_required():
    """
    API authentication helper for Super Admin only.
    """

    admin = get_current_admin()

    if not admin:
        return jsonify({
            "success": False,
            "authenticated": False,
            "message": "Admin login required."
        }), 401

    if not admin.is_super_admin:
        return jsonify({
            "success": False,
            "authenticated": True,
            "message": "Super Admin access required."
        }), 403

    return None


def require_super_admin(view_function):
    """
    Decorator for Super Admin-only routes.
    """

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        admin = get_current_admin()

        if not admin:
            return jsonify({
                "success": False,
                "authenticated": False,
                "message": "Admin login required."
            }), 401

        if not admin.is_super_admin:
            return jsonify({
                "success": False,
                "authenticated": True,
                "message": "Super Admin access required."
            }), 403

        return view_function(
            *args,
            **kwargs
        )

    return wrapped_view


# =========================================================
# ADMIN PANEL PAGE
# =========================================================

@admin_bp.route(
    "/panel",
    methods=["GET"]
)
def admin_panel():

    admin = get_current_admin()

    # -----------------------------------------------------
    # NOT LOGGED IN
    # -----------------------------------------------------

    if not admin:
        return render_template(
            "admin/login.html"
        )

    # -----------------------------------------------------
    # LOGGED IN
    # -----------------------------------------------------

    return render_template(
        "admin/dashboard.html",
        admin=admin
    )


# =========================================================
# ADMIN DASHBOARD STATUS
# =========================================================

@admin_bp.route(
    "/dashboard",
    methods=["GET"]
)
def dashboard():

    admin = get_current_admin()

    if not admin:
        return jsonify({
            "success": False,
            "authenticated": False,
            "message": "Admin login required."
        }), 401

    return jsonify({
        "success": True,
        "authenticated": True,
        "message": "Admin dashboard is working.",
        "admin": {
            "id": admin.id,
            "username": admin.username,
            "full_name": admin.full_name,
            "is_active": bool(admin.is_active),
            "is_super_admin": bool(admin.is_super_admin)
        }
    }), 200


# =========================================================
# ADMIN SESSION
# =========================================================

@admin_bp.route(
    "/session",
    methods=["GET"]
)
def admin_session():

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
        "admin": {
            "id": admin.id,
            "username": admin.username,
            "email": admin.email,
            "full_name": admin.full_name,
            "is_active": bool(admin.is_active),
            "is_super_admin": bool(admin.is_super_admin)
        }
    }), 200


# =========================================================
# ADMIN LOGOUT
# =========================================================

@admin_bp.route(
    "/logout",
    methods=["POST"]
)
def admin_logout():

    session.pop("admin_id", None)
    session.pop("admin_logged_in", None)

    return jsonify({
        "success": True,
        "authenticated": False,
        "message": "Admin logged out successfully."
    }), 200
