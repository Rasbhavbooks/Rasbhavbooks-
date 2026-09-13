from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    from app import models

    @app.route("/")
    def home():
        return "Rasbhav Books is running!"

    @app.route("/admin")
    def admin():
        return "Rasbhav Admin Panel"

    with app.app_context():
        db.create_all()

    return app
