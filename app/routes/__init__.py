from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import Config


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    # =====================================================
    # LOAD ALL DATABASE MODELS
    # =====================================================

    from app import models

    # =====================================================
    # PUBLIC ROUTES
    # =====================================================

    from app.routes.public import public_bp
    from app.routes.books import books_bp
    from app.routes.reader import reader_bp
    from app.routes.search import search_bp
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(reader_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)

    # =====================================================
    # ADMIN ROUTES
    # =====================================================

    from app.routes.admin import admin_bp
    from app.routes.admin_books import admin_books_bp
    from app.routes.admin_categories import admin_categories_bp
    from app.routes.admin_authors import admin_authors_bp
    from app.routes.admin_chapters import admin_chapters_bp

    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_books_bp)
    app.register_blueprint(admin_categories_bp)
    app.register_blueprint(admin_authors_bp)
    app.register_blueprint(admin_chapters_bp)

    # =====================================================
    # CREATE DATABASE TABLES
    # =====================================================

    with app.app_context():
        db.create_all()

    return app
