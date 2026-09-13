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
    
    app.register_blueprint(category_bp)
    app.register_blueprint(author_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_books_bp)
    app.register_blueprint(admin_chapters_bp)

    @app.route("/")
    def home():
        return "Rasbhav Books is running!"

    @app.route("/admin")
    def admin():
        return "Rasbhav Admin Panel"

    with app.app_context():
        db.create_all()

    return app
