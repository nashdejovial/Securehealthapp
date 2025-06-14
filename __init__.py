from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import timedelta
import os
from healthapp.extensions import db

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    from healthapp.models import User
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    
    # Configure secret key
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    # Configure session
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # Sessions last for 1 day
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=14)  # Remember me cookie lasts 14 days
    app.config['REMEMBER_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['REMEMBER_COOKIE_HTTPONLY'] = True
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///health.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.session_protection = 'strong'
    
    return app
