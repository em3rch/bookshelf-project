import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "default-secret")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///bookshelf.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_BOOKS_API_KEY = os.environ.get("GOOGLE_BOOKS_API_KEY", "")


    # os.environ.get - get environment variable value from
    # system environment variables dictionary (os.environ is the dictionary).
    # Fallback (second argument) is the value when first is not found.
