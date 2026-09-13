from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash

from app import db
from app.models.user import User
from app.models.bookmark import Bookmark
from app.models.favorite import Favorite
from app.models.reading_progress import ReadingProgress


user_bp = Blueprint(
    "user",
    __name__,
    url_prefix="/api/user"
)


# =========================================================
# REGISTER
# =========================================================

@user_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({
            "success": False,
            "message": "Username, email and password are required."
        }), 400

    if len(password) < 6:
        return jsonify({
            "success": False,
            "message": "Password must be at least 6 characters."
        }), 400

    if User.query.filter_by(username=username).first():
        return jsonify({
            "success": False,
            "message": "Username already exists."
        }), 409

    if User.query.filter_by(email=email).first():
        return jsonify({
            "success": False,
            "message": "Email already exists."
        }), 409

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        full_name=data.get("full_name", "").strip()
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Registration successful.",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name
        }
    }), 201


# =========================================================
# USER LOGIN
# =========================================================

@user_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    username_or_email = data.get(
        "username_or_email",
        ""
    ).strip()

    password = data.get("password", "")

    if not username_or_email or not password:
        return jsonify({
            "success": False,
            "message": "Username/email and password are required."
        }), 400

    user = User.query.filter(
        db.or_(
            User.username == username_or_email,
            User.email == username_or_email.lower()
        )
    ).filter(
        User.is_active.is_(True)
    ).first()

    from werkzeug.security import check_password_hash

    if not user or not check_password_hash(
        user.password_hash,
        password
    ):
        return jsonify({
            "success": False,
            "message": "Invalid username/email or password."
        }), 401

    session["user_id"] = user.id
    session["user_logged_in"] = True

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name
        }
    })


# =========================================================
# USER LOGOUT
# =========================================================

@user_bp.route("/logout", methods=["POST"])
def logout():

    session.pop("user_id", None)
    session.pop("user_logged_in", None)

    return jsonify({
        "success": True,
        "message": "Logout successful."
    })


# =========================================================
# CURRENT USER
# =========================================================

@user_bp.route("/me", methods=["GET"])
def current_user():

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "authenticated": False,
            "user": None
        })

    user = User.query.get(user_id)

    if not user or not user.is_active:
        session.clear()

        return jsonify({
            "authenticated": False,
            "user": None
        })

    return jsonify({
        "authenticated": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name
        }
    })


# =========================================================
# LIBRARY
# =========================================================

@user_bp.route("/library", methods=["GET"])
def library():

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Login required."
        }), 401

    favorites = Favorite.query.filter_by(
        user_id=user_id
    ).all()

    bookmarks = Bookmark.query.filter_by(
        user_id=user_id
    ).all()

    progress = ReadingProgress.query.filter_by(
        user_id=user_id
    ).all()

    return jsonify({
        "success": True,
        "favorites": [
            {
                "id": item.id,
                "book_id": item.book_id
            }
            for item in favorites
        ],
        "bookmarks": [
            {
                "id": item.id,
                "book_id": item.book_id,
                "chapter_id": item.chapter_id,
                "position": item.position,
                "note": item.note
            }
            for item in bookmarks
        ],
        "reading_progress": [
            {
                "id": item.id,
                "book_id": item.book_id,
                "chapter_id": item.chapter_id,
                "progress_percent": item.progress_percent,
                "last_position": item.last_position,
                "last_read_at": (
                    item.last_read_at.isoformat()
                    if item.last_read_at else None
                )
            }
            for item in progress
        ]
    })
