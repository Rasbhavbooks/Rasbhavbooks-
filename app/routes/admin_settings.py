# ============================================================
# RASBHAV BOOKS
# ADMIN SITE SETTINGS ROUTES / API
# ============================================================
#
# ADMIN PANEL
#      ↓
# SETTINGS API
#      ↓
# SITE SETTINGS DATABASE
#      ↓
# PUBLIC WEBSITE
#
# Features:
# - Admin authentication
# - Settings list
# - Search
# - Single setting
# - Create
# - Update
# - Delete
# - Text / Boolean / Integer / JSON values
# - Typed values
# - Bulk update
# - Safe validation
# - Rollback on errors
# ============================================================


from flask import Blueprint, request, jsonify

from app import db
from app.models.site_setting import SiteSetting

from app.routes.admin import admin_required


# ============================================================
# BLUEPRINT
# ============================================================

admin_settings_bp = Blueprint(
    "admin_settings",
    __name__,
    url_prefix="/api/admin/settings"
)


# ============================================================
# HELPERS
# ============================================================

ALLOWED_SETTING_TYPES = {
    "text",
    "textarea",
    "boolean",
    "integer",
    "json",
    "url",
    "email"
}


def clean_string(value, default=None):

    if value is None:
        return default

    value = str(value).strip()

    if not value:
        return default

    return value


def serialize_setting(setting):

    raw_value = setting.setting_value

    if setting.setting_type == "boolean":
        typed_value = setting.get_bool()

    elif setting.setting_type == "integer":
        typed_value = setting.get_int()

    elif setting.setting_type == "json":
        typed_value = setting.get_json()

    else:
        typed_value = setting.get_value()

    return {

        "id":
            setting.id,

        "setting_key":
            setting.setting_key,

        "setting_value":
            raw_value,

        "value":
            typed_value,

        "setting_type":
            setting.setting_type,

        "created_at": (
            setting.created_at.isoformat()
            if setting.created_at
            else None
        ),

        "updated_at": (
            setting.updated_at.isoformat()
            if setting.updated_at
            else None
        )
    }


# ============================================================
# NORMALIZE SETTING VALUE
# ============================================================

def normalize_value(
    value,
    setting_type
):

    setting_type = (
        setting_type or "text"
    ).strip().lower()

    if setting_type not in ALLOWED_SETTING_TYPES:

        raise ValueError(
            "Invalid setting_type. "
            "Allowed types: "
            + ", ".join(
                sorted(
                    ALLOWED_SETTING_TYPES
                )
            )
        )

    # --------------------------------------------------------
    # BOOLEAN
    # --------------------------------------------------------

    if setting_type == "boolean":

        if isinstance(
            value,
            bool
        ):

            return value

        if isinstance(
            value,
            int
        ):

            if value in (0, 1):
                return bool(value)

        if isinstance(
            value,
            str
        ):

            value = value.strip().lower()

            if value in (
                "true",
                "1",
                "yes",
                "on",
                "enabled"
            ):

                return True

            if value in (
                "false",
                "0",
                "no",
                "off",
                "disabled"
            ):

                return False

        raise ValueError(
            "Invalid boolean setting value."
        )

    # --------------------------------------------------------
    # INTEGER
    # --------------------------------------------------------

    if setting_type == "integer":

        try:

            return int(
                value
            )

        except (
            TypeError,
            ValueError
        ):

            raise ValueError(
                "Setting value must be an integer."
            )

    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    if setting_type == "json":

        if not isinstance(
            value,
            (dict, list)
        ):

            raise ValueError(
                "JSON setting value must be an object or array."
            )

        return value

    # --------------------------------------------------------
    # TEXT / URL / EMAIL / TEXTAREA
    # --------------------------------------------------------

    if value is None:
        return ""

    return str(
        value
    )


# ============================================================
# SAVE TYPED VALUE
# ============================================================

def save_typed_value(
    setting,
    value,
    setting_type
):

    normalized = normalize_value(
        value,
        setting_type
    )

    setting_type = (
        setting_type or "text"
    ).strip().lower()

    setting.setting_type = (
        setting_type
    )

    if setting_type == "boolean":

        setting.set_bool(
            normalized
        )

    elif setting_type == "integer":

        setting.set_int(
            normalized
        )

    elif setting_type == "json":

        setting.set_json(
            normalized
        )

    else:

        setting.set_value(
            normalized
        )


# ============================================================
# GET ALL SETTINGS
# ============================================================

@admin_settings_bp.route(
    "",
    methods=["GET"]
)
@admin_settings_bp.route(
    "/",
    methods=["GET"]
)
def get_settings():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        query = SiteSetting.query

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
                SiteSetting.setting_key.ilike(
                    pattern
                )
            )

        # ----------------------------------------------------
        # TYPE FILTER
        # ----------------------------------------------------

        setting_type = clean_string(
            request.args.get(
                "setting_type"
            )
        )

        if setting_type:

            query = query.filter(
                SiteSetting.setting_type
                == setting_type.lower()
            )

        settings = (
            query
            .order_by(
                SiteSetting.setting_key.asc()
            )
            .all()
        )

        return jsonify({

            "success":
                True,

            "count":
                len(settings),

            "settings": [

                serialize_setting(
                    setting
                )

                for setting in settings
            ]

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load settings.",

            "error":
                str(error)

        }), 500


# ============================================================
# GET SINGLE SETTING
# ============================================================

@admin_settings_bp.route(
    "/<string:setting_key>",
    methods=["GET"]
)
def get_setting(setting_key):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        setting_key = clean_string(
            setting_key
        )

        if not setting_key:

            return jsonify({

                "success":
                    False,

                "message":
                    "Setting key is required."

            }), 400

        setting = (
            SiteSetting.query
            .filter_by(
                setting_key=setting_key
            )
            .first()
        )

        if not setting:

            return jsonify({

                "success":
                    False,

                "message":
                    "Setting not found."

            }), 404

        return jsonify({

            "success":
                True,

            "setting":
                serialize_setting(
                    setting
                )

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to load setting.",

            "error":
                str(error)

        }), 500


# ============================================================
# CREATE SETTING
# ============================================================

@admin_settings_bp.route(
    "",
    methods=["POST"]
)
@admin_settings_bp.route(
    "/",
    methods=["POST"]
)
def create_setting():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(
        silent=True
    ) or {}

    try:

        # ----------------------------------------------------
        # KEY
        # ----------------------------------------------------

        setting_key = clean_string(
            data.get(
                "setting_key"
            )
        )

        if not setting_key:

            return jsonify({

                "success":
                    False,

                "message":
                    "Setting key is required."

            }), 400

        # ----------------------------------------------------
        # UNIQUE KEY
        # ----------------------------------------------------

        existing = (
            SiteSetting.query
            .filter_by(
                setting_key=setting_key
            )
            .first()
        )

        if existing:

            return jsonify({

                "success":
                    False,

                "message":
                    "Setting key already exists."

            }), 409

        # ----------------------------------------------------
        # TYPE
        # ----------------------------------------------------

        setting_type = clean_string(
            data.get(
                "setting_type"
            ),
            "text"
        ).lower()

        if setting_type not in ALLOWED_SETTING_TYPES:

            return jsonify({

                "success":
                    False,

                "message":
                    "Invalid setting_type.",

                "allowed_types":
                    sorted(
                        ALLOWED_SETTING_TYPES
                    )

            }), 400

        # ----------------------------------------------------
        # VALUE
        # ----------------------------------------------------

        value = data.get(
            "value",
            data.get(
                "setting_value"
            )
        )

        setting = SiteSetting(
            setting_key=setting_key,
            setting_type=setting_type
        )

        save_typed_value(
            setting,
            value,
            setting_type
        )

        db.session.add(
            setting
        )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Setting created successfully.",

            "setting":
                serialize_setting(
                    setting
                )

        }), 201

    except ValueError as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                str(error)

        }), 400

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to create setting.",

            "error":
                str(error)

        }), 500


# ============================================================
# UPDATE SETTING
# ============================================================

@admin_settings_bp.route(
    "/<string:setting_key>",
    methods=["PUT", "PATCH"]
)
def update_setting(setting_key):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(
        silent=True
    ) or {}

    try:

        setting = (
            SiteSetting.query
            .filter_by(
                setting_key=setting_key
            )
            .first()
        )

        if not setting:

            return jsonify({

                "success":
                    False,

                "message":
                    "Setting not found."

            }), 404

        # ----------------------------------------------------
        # NEW KEY
        # ----------------------------------------------------

        if "setting_key" in data:

            new_key = clean_string(
                data.get(
                    "setting_key"
                )
            )

            if not new_key:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Setting key cannot be empty."

                }), 400

            existing = (
                SiteSetting.query
                .filter(
                    SiteSetting.setting_key
                    == new_key,

                    SiteSetting.id
                    != setting.id
                )
                .first()
            )

            if existing:

                return jsonify({

                    "success":
                        False,

                    "message":
                        "Setting key already exists."

                }), 409

            setting.setting_key = new_key

        # ----------------------------------------------------
        # TYPE
        # ----------------------------------------------------

        setting_type = data.get(
            "setting_type",
            setting.setting_type
        )

        setting_type = clean_string(
            setting_type,
            "text"
        ).lower()

        if setting_type not in ALLOWED_SETTING_TYPES:

            return jsonify({

                "success":
                    False,

                "message":
                    "Invalid setting_type.",

                "allowed_types":
                    sorted(
                        ALLOWED_SETTING_TYPES
                    )

            }), 400

        # ----------------------------------------------------
        # VALUE
        # ----------------------------------------------------

        has_value = (
            "value" in data
            or
            "setting_value" in data
        )

        if has_value:

            value = data.get(
                "value",
                data.get(
                    "setting_value"
                )
            )

            save_typed_value(
                setting,
                value,
                setting_type
            )

        else:

            setting.setting_type = (
                setting_type
            )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Setting updated successfully.",

            "setting":
                serialize_setting(
                    setting
                )

        }), 200

    except ValueError as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                str(error)

        }), 400

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to update setting.",

            "error":
                str(error)

        }), 500


# ============================================================
# BULK UPDATE SETTINGS
# ============================================================

@admin_settings_bp.route(
    "/bulk",
    methods=["PUT", "PATCH", "POST"]
)
def bulk_update_settings():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(
        silent=True
    ) or {}

    try:

        settings_data = data.get(
            "settings"
        )

        if not isinstance(
            settings_data,
            list
        ):

            return jsonify({

                "success":
                    False,

                "message":
                    "settings must be an array."

            }), 400

        updated = []

        for item in settings_data:

            if not isinstance(
                item,
                dict
            ):

                continue

            setting_key = clean_string(
                item.get(
                    "setting_key"
                )
            )

            if not setting_key:

                raise ValueError(
                    "Every setting must have a setting_key."
                )

            setting = (
                SiteSetting.query
                .filter_by(
                    setting_key=setting_key
                )
                .first()
            )

            if not setting:

                setting = SiteSetting(
                    setting_key=setting_key
                )

                db.session.add(
                    setting
                )

            setting_type = clean_string(
                item.get(
                    "setting_type"
                ),
                setting.setting_type or "text"
            ).lower()

            value = item.get(
                "value",
                item.get(
                    "setting_value"
                )
            )

            save_typed_value(
                setting,
                value,
                setting_type
            )

            updated.append(
                setting
            )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Settings updated successfully.",

            "count":
                len(updated),

            "settings": [

                serialize_setting(
                    setting
                )

                for setting in updated
            ]

        }), 200

    except ValueError as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                str(error)

        }), 400

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to update settings.",

            "error":
                str(error)

        }), 500


# ============================================================
# DELETE SETTING
# ============================================================

@admin_settings_bp.route(
    "/<string:setting_key>",
    methods=["DELETE"]
)
def delete_setting(setting_key):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    try:

        setting = (
            SiteSetting.query
            .filter_by(
                setting_key=setting_key
            )
            .first()
        )

        if not setting:

            return jsonify({

                "success":
                    False,

                "message":
                    "Setting not found."

            }), 404

        deleted_key = (
            setting.setting_key
        )

        db.session.delete(
            setting
        )

        db.session.commit()

        return jsonify({

            "success":
                True,

            "message":
                "Setting deleted successfully.",

            "setting_key":
                deleted_key

        }), 200

    except Exception as error:

        db.session.rollback()

        return jsonify({

            "success":
                False,

            "message":
                "Unable to delete setting.",

            "error":
                str(error)

        }), 500
