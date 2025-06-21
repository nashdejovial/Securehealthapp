from flask import Flask
from .config import config
from .extensions import db, migrate, login_manager

def create_app(config_name='default'):
    """
    Application factory function.
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize Flask extensions


    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    

    # Configure login manager
    login_manager.login_view = 'login' # The endpoint for the login route
    login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
    login_manager.login_message_category = "info"

    # Import and register routes
    with app.app_context():
        from . import routes
        routes.register_routes(app, db)

    # Import models to be seen by Flask-Migrate
    from . import models

    return app

