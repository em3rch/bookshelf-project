from flask import Flask, render_template
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

    @app.cli.command("init-db")
    def init_db():
        """Create DB tables"""
        db.create_all()
        print("Database has been initialized.")


    # Registering blueprints
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    from app.routes.books import books_bp
    app.register_blueprint(books_bp)
    from app.routes.api import api_bp
    app.register_blueprint(api_bp)

    @app.errorhandler(403)
    def forbidden(error):
        return render_template(
            "errors/403.html"
        ), 403
    

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template(
            "errors/404.html"
        ), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        db.session.rollback()
        
        return render_template(
            "errors/500.html"
        ), 500
    

    return app

