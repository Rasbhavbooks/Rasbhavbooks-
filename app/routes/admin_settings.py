from flask import Blueprint, request, jsonify, session

from app import db
from app.models.site_setting import SiteSetting


admin_settings_bp = Blueprint(
    "admin_settings",
    __name__,
    url_prefix="/api/admin/settings"
)


def admin_required():
    if not session.get("admin_id"):
        return jsonify({
            "success": False,
            "message": "Admin login required."
        }), 401

    return None


# =========================================================
# GET ALL SETTINGS
# =========================================================

@admin_settings_bp.route("", methods=["GET"])
def get_settings():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    settings = SiteSetting.query.order_by(
        SiteSetting.setting_key.asc()
    ).all()

    return jsonify({
        "success": True,
        "count": len(settings),
        "settings": [
            {
                "id": setting.id,
                "setting_key": setting.setting_key,
                "setting_value": setting.setting_value,
                "setting_type": setting.setting_type,
                "created_at": (
                    setting.created_at.isoformat()
                    if setting.created_at else None
                ),
                "updated_at": (
                    setting.updated_at.isoformat()
                    if setting.updated_at else None
                )
            }
            for setting in settings
        ]
    })


# =========================================================
# GET SINGLE SETTING
# =========================================================

@admin_settings_bp.route("/<string:setting_key>", methods=["GET"])
def get_setting(setting_key):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    setting = SiteSetting.query.filter_by(
        setting_key=setting_key
    ).first_or_404()

    return jsonify({
        "success": True,
        "setting": {
            "id": setting.id,
            "setting_key": setting.setting_key,
            "setting_value": setting.setting_value,
            "setting_type": setting.setting_type
        }
    })


# =========================================================
# CREATE SETTING
# =========================================================

@admin_settings_bp.route("", methods=["POST"])
def create_setting():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}

    setting_key = data.get("setting_key", "").strip()

    if not setting_key:
        return jsonify({
            "success": False,
            "message": "Setting key is required."
        }), 400

    existing = SiteSetting.query.filter_by(
        setting_key=setting_key
    ).first()

    if existing:
        return jsonify({
            "success": False,
            "message": "Setting key already exists."
        }), 409

    setting = SiteSetting(
        setting_key=setting_key,
        setting_value=data.get("setting_value"),
        setting_type=data.get("setting_type", "text")
    )

    db.session.add(setting)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Setting created successfully.",
        "setting_id": setting.id
    }), 201


# =========================================================
# UPDATE SETTING
# =========================================================

@admin_settings_bp.route("/<string:setting_key>", methods=["PUT"])
def update_setting(setting_key):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    setting = SiteSetting.query.filter_by(
        setting_key=setting_key
    ).first_or_404()

    data = request.get_json(silent=True) or {}

    if "setting_value" in data:
        setting.setting_value = data["setting_value"]

    if "setting_type" in data:
        setting.setting_type = data["setting_type"]

    if "setting_key" in data:

        new_key = str(
            data["setting_key"]
        ).strip()

        if not new_key:
            return jsonify({
                "success": False,
                "message": "Setting key cannot be empty."
            }), 400

        existing = SiteSetting.query.filter(
            SiteSetting.setting_key == new_key,
            SiteSetting.id != setting.id
        ).first()

        if existing:
            return jsonify({
                "success": False,
                "message": "Setting key already exists."
            }), 409

        setting.setting_key = new_key

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Setting updated successfully.",
        "setting_id": setting.id
    })


# =========================================================
# DELETE SETTING
# =========================================================

@admin_settings_bp.route("/<string:setting_key>", methods=["DELETE"])
def delete_setting(setting_key):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    setting = SiteSetting.query.filter_by(
        setting_key=setting_key
    ).first_or_404()

    db.session.delete(setting)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Setting deleted successfully."
    })
