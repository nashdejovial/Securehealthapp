from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)  # Increased length for hash
    role = db.Column(db.String(20), nullable=False)  # 'patient', 'doctor', 'receptionist', 'hr'
    is_active = db.Column(db.Boolean, default=True)

    # Relationships - removed duplicate backrefs
    patient = db.relationship('Patient', backref=db.backref('user', uselist=False), uselist=False)
    doctor = db.relationship('Doctor', backref=db.backref('user', uselist=False), uselist=False)
    receptionist = db.relationship('Receptionist', backref=db.backref('user', uselist=False), uselist=False)
    hr = db.relationship('HR', backref=db.backref('user', uselist=False), uselist=False)
    lab_tech = db.relationship('LabTech', backref=db.backref('user', uselist=False), uselist=False)

    def set_password(self, password):
        if not password:
            raise ValueError("Password cannot be empty")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    phone = db.Column(db.String(12), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    gender = db.Column(db.String(30))
    address = db.Column(db.String(200))
    age = db.Column(db.Integer, default=0)
    blood = db.Column(db.String(10))
    medical = db.Column(db.String(100))
    case = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    # Relationships
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    prescriptions = db.relationship('Prescription', backref='patient', lazy=True)
    invoice = db.relationship('Invoice', backref='patient', uselist=False)
    lab_results = db.relationship('LabResult', backref='patient', lazy=True)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    phone = db.Column(db.String(12), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    gender = db.Column(db.String(30))
    address = db.Column(db.String(200))
    age = db.Column(db.Integer, default=0)
    blood = db.Column(db.String(10))
    status = db.Column(db.Boolean, default=False)
    department = db.Column(db.String(30), default='')
    attendance = db.Column(db.Integer, default=0)
    salary = db.Column(db.Integer, default=10000)
    specialization = db.Column(db.String(100))  # Added specialization field
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    # Relationships
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)
    prescriptions = db.relationship('Prescription', backref='doctor', lazy=True)
    schedules = db.relationship('DoctorSchedule', backref='doctor', lazy=True)
    lab_results = db.relationship('LabResult', backref='doctor', lazy=True)

class Receptionist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    phone = db.Column(db.String(12), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    address = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    # Removed duplicate relationship

class HR(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    phone = db.Column(db.String(12), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    # Removed duplicate relationship

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    time = db.Column(db.String(40), nullable=False)
    date = db.Column(db.String(40), nullable=False)
    status = db.Column(db.Boolean, default=False)
    prescriptions = db.relationship('Prescription', backref='appointment', lazy=True)

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prescription = db.Column(db.String(200), nullable=False)
    symptoms = db.Column(db.String(200), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    prescribed_date = db.Column(db.DateTime, default=datetime.utcnow)
    outstanding = db.Column(db.Integer, default=0)
    paid = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=0)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), unique=True, nullable=False)
    outstanding = db.Column(db.String(10), default='0')
    paid = db.Column(db.String(10), default='0')

class LabResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    lab_tech_id = db.Column(db.Integer, db.ForeignKey('lab_tech.id'), nullable=True)  # Added lab technician
    test_name = db.Column(db.String(100), nullable=False)
    test_date = db.Column(db.DateTime, default=datetime.utcnow)
    result_date = db.Column(db.DateTime)
    result_value = db.Column(db.String(200))
    reference_range = db.Column(db.String(100))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='ordered')  # ordered, processing, completed, reviewed
    file_path = db.Column(db.String(200))  # For storing lab result files/images
    doctor_notes = db.Column(db.Text)  # Added for doctor's review notes
    reviewed_at = db.Column(db.DateTime)  # Added to track when doctor reviewed the result

class LabTech(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    phone = db.Column(db.String(12), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    address = db.Column(db.String(200))  # Added address field
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    lab_results = db.relationship('LabResult', backref='lab_tech', lazy=True)

class DoctorSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0-6 for Monday-Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    max_patients = db.Column(db.Integer, default=10)
    break_start = db.Column(db.Time)
    break_end = db.Column(db.Time)

def init_models(db):
    """Initialize models and return them."""
    return User, Patient, Doctor, Receptionist, HR, Appointment, Prescription, Invoice, LabResult, DoctorSchedule, LabTech 