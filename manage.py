from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from app import app, db

migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Stamp the database with the latest migration
        upgrade() 