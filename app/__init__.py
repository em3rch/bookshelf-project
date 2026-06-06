from flask import Flask
from app.config import Config
from app.extensions import db, login_manager


def create_app():
    app = Flask(__name__)

    """
    Tells Flask to read Config class and look
    for all the uppercase variables inside that class and
    copy them into Flask's internal configuration dictionary.
    Flask, then, stores config variables in a dictionary-like object
    called app.config. You can access it anywhere in this app. Or you
    can use 'from flask import current_app' (in case of circular imports).
    current_app points to the active Flask app, so you can grab settings 
    safely from any file.
    """
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)


    return app

