from flask import Blueprint, render_template, jsonify, session


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
# ADMIN PANEL PAGE
# =========================================================

@admin_bp.route("/panel", methods=["GET"])
def admin_panel():
    return render_template(
        "admin/dashboard.html"
    )


# =========================================================
# ADMIN DASHBOARD STATUS
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
