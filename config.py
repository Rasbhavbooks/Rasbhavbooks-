import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "rasbhav-development-secret-change-this"
    )

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///rasbhav.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
