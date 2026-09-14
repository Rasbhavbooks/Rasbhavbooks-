# =========================================================
# RASBHAV BOOKS
# FLASK APPLICATION FACTORY
# app/__init__.py
# =========================================================

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import Config


# =========================================================
# DATABASE
# =========================================================

db = SQLAlchemy()


# =========================================================
# APPLICATION FACTORY
# =========================================================

def create_app():

    app = Flask(__name__)

    # -----------------------------------------------------
    # CONFIGURATION
    # -----------------------------------------------------

    app.config.from_object(Config)

    # -----------------------------------------------------
    # DATABASE
    # -----------------------------------------------------

    db.init_app(app)

    # -----------------------------------------------------
    # LOAD ALL MODELS
    # -----------------------------------------------------

    from app import models


    # =====================================================
    # PUBLIC ROUTES
    # =====================================================

    from app.routes.public import public_bp
    from app.routes.books import books_bp
    from app.routes.reader import reader_bp
    from app.routes.category import category_bp
    from app.routes.author import author_bp
    from app.routes.search import search_bp
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp


    # =====================================================
    # ADMIN ROUTES
    # =====================================================

    from app.routes.admin import admin_bp
    from app.routes.admin_dashboard import admin_dashboard_bp
    from app.routes.admin_books import admin_books_bp
    from app.routes.admin_chapters import admin_chapters_bp
    from app.routes.admin_categories import admin_categories_bp
    from app.routes.admin_authors import admin_authors_bp
    from app.routes.admin_users import admin_users_bp
    from app.routes.admin_settings import admin_settings_bp
    from app.routes.admin_seo import admin_seo_bp
    from app.routes.admin_media import admin_media_bp
    from app.routes.admin_pages import admin_pages_bp
    from app.routes.admin_menu import admin_menu_bp


    # =====================================================
    # REGISTER PUBLIC BLUEPRINTS
    # =====================================================

    app.register_blueprint(public_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(reader_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(author_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)


    # =====================================================
    # REGISTER ADMIN BLUEPRINTS
    # =====================================================

    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_dashboard_bp)
    app.register_blueprint(admin_books_bp)
    app.register_blueprint(admin_chapters_bp)
    app.register_blueprint(admin_categories_bp)
    app.register_blueprint(admin_authors_bp)
    app.register_blueprint(admin_users_bp)
    app.register_blueprint(admin_settings_bp)
    app.register_blueprint(admin_seo_bp)
    app.register_blueprint(admin_media_bp)
    app.register_blueprint(admin_pages_bp)
    app.register_blueprint(admin_menu_bp)


    # =====================================================
    # DATABASE INITIALIZATION
    # =====================================================

    with app.app_context():
        db.create_all()


    # =====================================================
    # APPLICATION RETURN
    # =====================================================

    return app
