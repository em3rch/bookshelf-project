from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


# It should be created before it is connected to Flask app
# in order to prevent circular imports (imports in both ways).
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = "auth.login_handler" # redirect user to 'login' route that is being located under 'auth' blueprint.l

