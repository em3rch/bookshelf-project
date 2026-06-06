from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


# It should be created before it is connected to Flask app
# in order to prevent circular imports (imports in both ways).
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = "auth.login" # redirect user to 'login' route that is being located under 'auth' blueprint.


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

