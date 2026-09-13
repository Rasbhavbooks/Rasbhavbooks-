from flask import Blueprint, request, jsonify, session

from app import db
from app.models.author import Author


admin_authors_bp = Blueprint(
    "admin_authors",
    __name__,
    url_prefix="/api/admin/authors"
)


def admin_required():
    if not session.get("admin_id"):
        return jsonify({
            "success": False,
            "message": "Admin login required."
        }), 401

    return None


@admin_authors_bp.route("", methods=["GET"])
def get_authors():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    authors = Author.query.order_by(
        Author.name.asc()
    ).all()

    return jsonify({
        "success": True,
        "count": len(authors),
        "authors": [
            {
                "id": author.id,
                "name": author.name,
                "slug": author.slug,
                "biography": author.biography,
                "profile_image": author.profile_image,
                "social_links": author.social_links,
                "created_at": (
                    author.created_at.isoformat()
                    if author.created_at else None
                ),
                "updated_at": (
                    author.updated_at.isoformat()
                    if author.updated_at else None
                )
            }
            for author in authors
        ]
    })


@admin_authors_bp.route("/<int:author_id>", methods=["GET"])
def get_author(author_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    author = Author.query.get_or_404(author_id)

    return jsonify({
        "success": True,
        "author": {
            "id": author.id,
            "name": author.name,
            "slug": author.slug,
            "biography": author.biography,
            "profile_image": author.profile_image,
            "social_links": author.social_links
        }
    })


@admin_authors_bp.route("", methods=["POST"])
def create_author():

    auth_error = admin_required()

    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    slug = data.get("slug", "").strip()

    if not name:
        return jsonify({
            "success": False,
            "message": "Author name is required."
        }), 400

    if not slug:
        return jsonify({
            "success": False,
            "message": "Author slug is required."
        }), 400

    if Author.query.filter_by(slug=slug).first():
        return jsonify({
            "success": False,
            "message": "Author slug already exists."
        }), 409

    author = Author(
        name=name,
        slug=slug,
        biography=data.get("biography"),
        profile_image=data.get("profile_image"),
        social_links=data.get("social_links")
    )

    db.session.add(author)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Author created successfully.",
        "author_id": author.id
    }), 201


@admin_authors_bp.route("/<int:author_id>", methods=["PUT"])
def update_author(author_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    author = Author.query.get_or_404(author_id)

    data = request.get_json(silent=True) or {}

    if "name" in data:

        name = str(data["name"]).strip()

        if not name:
            return jsonify({
                "success": False,
                "message": "Author name cannot be empty."
            }), 400

        author.name = name

    if "slug" in data:

        slug = str(data["slug"]).strip()

        if not slug:
            return jsonify({
                "success": False,
                "message": "Author slug cannot be empty."
            }), 400

        existing = Author.query.filter(
            Author.slug == slug,
            Author.id != author.id
        ).first()

        if existing:
            return jsonify({
                "success": False,
                "message": "Author slug already exists."
            }), 409

        author.slug = slug

    if "biography" in data:
        author.biography = data["biography"]

    if "profile_image" in data:
        author.profile_image = data["profile_image"]

    if "social_links" in data:
        author.social_links = data["social_links"]

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Author updated successfully.",
        "author_id": author.id
    })


@admin_authors_bp.route("/<int:author_id>", methods=["DELETE"])
def delete_author(author_id):

    auth_error = admin_required()

    if auth_error:
        return auth_error

    author = Author.query.get_or_404(author_id)

    db.session.delete(author)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Author deleted successfully."
    })
