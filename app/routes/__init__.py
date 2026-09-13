from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import Config


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    # Load all database models
    from app import models

    # Register routes
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

    with app.app_context():
        db.create_all()

    return app
