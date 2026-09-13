from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    from app import models

    from app.routes.category import category_bp
    from app.routes.author import author_bp
    from app.routes.search import search_bp
    from app.routes.admin import admin_bp
    from app.routes.user import user_bp
    from app.routes.admin_books import admin_books_bp
    from app.routes.admin_chapters import admin_chapters_bp 
    from app.routes.admin_categories import admin_categories_bp
    from app.routes.admin_authors import admin_authors_bp
    from app.routes.admin_users import admin_users_bp
    from app.routes.admin_settings import admin_settings_bp
    from app.routes.admin_seo import admin_seo_bp
    from app.routes.admin_media import admin_media_bp
    
    app.register_blueprint(category_bp)
    app.register_blueprint(author_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_books_bp)
    app.register_blueprint(admin_chapters_bp)
    app.register_blueprint(admin_categories_bp)
    app.register_blueprint(admin_authors_bp)
    app.register_blueprint(admin_users_bp)
    app.register_blueprint(admin_settings_bp)
    app.register_blueprint(admin_seo_bp)
    app.register_blueprint(admin_media_bp)

    @app.route("/")
    def home():
        return "Rasbhav Books is running!"

    @app.route("/admin")
    def admin():
        return "Rasbhav Admin Panel"

    with app.app_context():
        db.create_all()

    return app
