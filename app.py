from flask import Flask, render_template
from config import config
from extensions import init_extensions, db, login_manager, csrf
from flask_migrate import Migrate
import os
import logging
from logging.handlers import RotatingFileHandler
from models import User, Patient, Doctor, Receptionist, HR, Appointment, Prescription, Invoice, LabTech, LabResult, DoctorSchedule
from routes import register_routes
from init_db import init_db
from flask_login import LoginManager

def create_app(config_name='default'):
    """Application factory function."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Ensure CSRF protection is properly configured
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_SECRET_KEY'] = app.config['SECRET_KEY']
    
    # Set up logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/healthapp.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('HealthApp startup')
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    init_extensions(app)
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)
    
    # Initialize LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.session_protection = 'strong'
    
    # Import routes and register them
    with app.app_context():
        register_routes(app, db)
        
        @login_manager.user_loader
        def load_user(user_id):
            try:
                return User.query.get(int(user_id))
            except Exception as e:
                app.logger.error(f"Error loading user: {str(e)}")
                return None
        
        # Error handlers
        @app.errorhandler(404)
        def not_found_error(error):
            return render_template('errors/404.html'), 404

        @app.errorhandler(500)
        def internal_error(error):
            db.session.rollback()
            return render_template('errors/500.html'), 500
        
        # Add security headers in production
        if not app.debug and not app.testing:
            @app.after_request
            def add_security_headers(response):
                for header, value in app.config.get('SECURITY_HEADERS', {}).items():
                    response.headers[header] = value
                return response
        
        # Initialize CLI commands
        from cli import init_cli
        init_cli(app, db)
        
        # Initialize database
        init_db(app)
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 