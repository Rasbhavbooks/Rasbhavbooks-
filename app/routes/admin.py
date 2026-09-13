from flask import Blueprint, jsonify, session


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/api/admin"
)


# =========================================================
# ADMIN AUTH CHECK
# =========================================================

def admin_required():
    admin_id = session.get("admin_id")

    if not admin_id:
        return jsonify({
            "success": False,
            "message": "Admin login required."
        }), 401

    return None


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@admin_bp.route("/dashboard", methods=["GET"])
def dashboard():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    return jsonify({
        "success": True,
        "message": "Admin dashboard is working."
    })
