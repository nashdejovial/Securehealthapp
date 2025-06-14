from app import app, db
from models import User, Patient, Doctor, Receptionist, HR, Appointment, Prescription, Invoice
from sqlalchemy_utils import database_exists, create_database

def init_db():
    with app.app_context():
        # Create database if it doesn't exist
        if not database_exists(db.engine.url):
            create_database(db.engine.url)
            print("Database created successfully!")
        
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")

if __name__ == "__main__":
    init_db() 