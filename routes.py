from flask import render_template, redirect, url_for, flash, request, send_file, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, time
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TimeField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, NumberRange
from models import User, Patient, Doctor, Receptionist, HR, Appointment, Prescription, Invoice, LabResult, DoctorSchedule, LabTech
import os
import pdfkit
from forms import LabTestForm, ProcessLabResultForm
from werkzeug.datastructures import MultiDict


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


def register_routes(app, db):
    # Home route
    @app.route('/')
    def home():
        return render_template('home.html', user=None)

    # Register route
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            try:
                # Get form data
                username = request.form.get('username')
                password = request.form.get('pass1')
                role = request.form.get('post')
                name = request.form.get('name')
                email = request.form.get('email')
                phone = request.form.get('phone')

                # Validate required fields
                if not all([username, password, role, name, email, phone]):
                    flash('All fields are required')
                    return redirect(url_for('register'))

                # Convert role to lowercase and handle special cases
                role = role.lower()
                if role == 'lab technician':
                    role = 'lab_tech'

                # Check if username already exists
                if User.query.filter_by(username=username).first():
                    flash('Username already exists')
                    return redirect(url_for('register'))

                # Check if email already exists
                if any([
                    Patient.query.filter_by(email=email).first(),
                    Doctor.query.filter_by(email=email).first(),
                    Receptionist.query.filter_by(email=email).first(),
                    HR.query.filter_by(email=email).first(),
                    LabTech.query.filter_by(email=email).first()
                ]):
                    flash('Email already exists')
                    return redirect(url_for('register'))

                # Check if phone already exists
                if any([
                    Patient.query.filter_by(phone=phone).first(),
                    Doctor.query.filter_by(phone=phone).first(),
                    Receptionist.query.filter_by(phone=phone).first(),
                    HR.query.filter_by(phone=phone).first(),
                    LabTech.query.filter_by(phone=phone).first()
                ]):
                    flash('Phone number already exists')
                    return redirect(url_for('register'))

                # Create user
                user = User(username=username, role=role)
                user.set_password(password)
                db.session.add(user)

                # Common fields for all roles
                common_fields = {
                    'name': name,
                    'phone': phone,
                    'email': email,
                    'user': user
                }

                # Additional fields for Patient and Doctor
                if role in ['patient', 'doctor']:
                    gender = request.form.get('gender')
                    age = request.form.get('age')
                    blood = request.form.get('blood')
                    address = request.form.get('address')

                    if not all([gender, age, blood]):
                        flash('All fields are required for Patient/Doctor registration')
                        return redirect(url_for('register'))

                    common_fields.update({
                        'gender': gender,
                        'address': address,
                        'age': age,
                        'blood': blood
                    })

                try:
                    if role == 'patient':
                        medical = request.form.get('medical')
                        case = request.form.get('case')
                        
                        patient = Patient(
                            **common_fields,
                            medical=medical,
                            case=case
                        )
                        db.session.add(patient)

                        # Create invoice for patient
                        invoice = Invoice(patient=patient)
                        db.session.add(invoice)

                    elif role == 'doctor':
                        department = request.form.get('department')
                        if not department:
                            flash('Department is required for Doctor registration')
                            return redirect(url_for('register'))

                        doctor = Doctor(
                            **common_fields,
                            department=department,
                            status=False,  # New doctors start as inactive
                            attendance=0,  # Initialize attendance to 0
                            salary=10000  # Default salary
                        )
                        db.session.add(doctor)

                    elif role == 'receptionist':
                        address = request.form.get('address', '')
                        receptionist = Receptionist(
                            **common_fields,
                            address=address
                        )
                        db.session.add(receptionist)

                    elif role == 'hr':
                        hr = HR(**common_fields)
                        db.session.add(hr)
                        
                    elif role == 'lab_tech':
                        address = request.form.get('address', '')
                        app.logger.info(f"Creating LabTech with data: {common_fields}, address: {address}")
                        try:
                            # First commit the user to get the ID
                            db.session.commit()
                            
                            lab_tech = LabTech(
                                name=name,
                                phone=phone,
                                email=email,
                                address=address,
                                user_id=user.id
                            )
                            db.session.add(lab_tech)
                            app.logger.info(f"LabTech object created successfully for user {username}")
                        except Exception as e:
                            db.session.rollback()
                            app.logger.error(f"Error creating LabTech object: {str(e)}")
                            app.logger.error(f"Common fields: {common_fields}")
                            app.logger.error(f"Address: {address}")
                            raise

                    # Commit all changes
                    try:
                        db.session.commit()
                        app.logger.info(f"Registration successful for user {username} with role {role}")
                        flash('Registration successful')
                        return redirect(url_for('login'))
                    except Exception as e:
                        db.session.rollback()
                        app.logger.error(f"Database commit error during registration: {str(e)}")
                        app.logger.error(f"Error type: {type(e)}")
                        app.logger.error(f"Error args: {e.args}")
                        flash('Error saving registration data. Please try again.')
                        return redirect(url_for('register'))

                except Exception as e:
                    db.session.rollback()
                    app.logger.error(f"Error during role-specific registration: {str(e)}")
                    app.logger.error(f"Error type: {type(e)}")
                    app.logger.error(f"Error args: {e.args}")
                    flash('Error saving registration data. Please try again.')
                    return redirect(url_for('register'))

            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Registration error: {str(e)}")
                app.logger.error(f"Error type: {type(e)}")
                app.logger.error(f"Error args: {e.args}")
                flash('An error occurred during registration. Please try again.')
                return redirect(url_for('register'))

        return render_template('register.html')

    # Login route
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
            
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                if user.role == 'patient':
                    return redirect(url_for('dashboard', user_type='P'))
                elif user.role == 'doctor':
                    return redirect(url_for('dashboard', user_type='D'))
                elif user.role == 'receptionist':
                    return redirect(url_for('receptionist_dashboard', user_type='R'))
                elif user.role == 'hr':
                    return redirect(url_for('hr_dashboard'))
                elif user.role == 'lab_tech':
                    return redirect(url_for('lab_tech_results'))
            flash('Invalid username or password')
            return redirect(url_for('login'))
        return render_template('login.html', form=form)

    @app.route('/verify_phone', methods=['GET', 'POST'])
    def verify_phone():
        if request.method == 'POST':
            verification_code = request.form.get('verification_code')
            user_id = session.get('user_id')
            
            if not user_id or not verification_code:
                flash('Invalid verification attempt')
                return redirect(url_for('login'))
            
            user = User.query.get(user_id)
            if not user:
                flash('User not found')
                return redirect(url_for('login'))
            
            if user.verify_code(verification_code):
                login_user(user)
                flash('Phone verification successful')
                return redirect(url_for('hr_dashboard'))
            else:
                flash('Invalid or expired verification code')
                return redirect(url_for('verify_phone'))
        
        return render_template('verify_phone.html')

    @app.route('/resend_verification_code', methods=['POST'])
    def resend_verification_code():
        user_id = session.get('user_id')
        if not user_id:
            return {'success': False, 'error': 'No user found'}, 400
        
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'error': 'User not found'}, 404
        
        try:
            verification_code = user.generate_verification_code()
            # In a real application, you would send this code via SMS
            # For now, we'll just store it in the session for testing
            session['verification_code'] = verification_code
            return {'success': True}
        except Exception as e:
            app.logger.error(f"Error generating verification code: {str(e)}")
            return {'success': False, 'error': str(e)}, 500

    # Logout route
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    # Dashboard route
    @app.route('/dashboard/<user_type>')
    @login_required
    def dashboard(user_type):
        if current_user.role == 'patient':
            # Get patient's appointments
            appointments = Appointment.query.filter_by(patient=current_user.patient).order_by(
                Appointment.date.desc()).all()
            today = datetime.now().strftime('%Y-%m-%d')

            upcoming_appointments = len([a for a in appointments if a.date >= today])
            past_appointments = len([a for a in appointments if a.date < today])
            total_prescriptions = len(current_user.patient.prescriptions)
            recent_appointments = appointments[:5]  # Get 5 most recent appointments

            return render_template('patient_dashboard.html',
                                   user=user_type,
                                   upcoming_appointments=upcoming_appointments,
                                   past_appointments=past_appointments,
                                   total_prescriptions=total_prescriptions,
                                   recent_appointments=recent_appointments)

        elif current_user.role == 'doctor':
            # Get doctor's appointments for today
            today = datetime.now().strftime('%Y-%m-%d')
            today_appointments_list = Appointment.query.filter_by(
                doctor=current_user.doctor,
                date=today
            ).all()

            total_appointments = len(today_appointments_list)
            pending_appointments = len([a for a in today_appointments_list if not a.status])
            completed_appointments = len([a for a in today_appointments_list if a.status])

            return render_template('doctor_dashboard.html',
                                   user=user_type,
                                   today_appointments=total_appointments,
                                   pending_appointments=pending_appointments,
                                   completed_appointments=completed_appointments,
                                   today_appointments_list=today_appointments_list)

        elif current_user.role == 'hr':
            return redirect(url_for('hr_dashboard'))

        elif current_user.role == 'receptionist':
            return redirect(url_for('receptionist_dashboard', user_type=user_type))

        return render_template('home.html', user=user_type)

    # Receptionist dashboard route
    @app.route('/receptionist_dashboard/<user_type>')
    @login_required
    def receptionist_dashboard(user_type):
        try:
            if current_user.role != 'receptionist':
                flash('Unauthorized access')
                return redirect(url_for('home'))

            today = datetime.now().strftime('%Y-%m-%d')
            appointments = Appointment.query.filter_by(date=today).all()
            today_appointments = len(appointments)
            pending_appointments = len([a for a in appointments if not a.status])
            completed_appointments = len([a for a in appointments if a.status])

            return render_template('receptionist_dashboard.html',
                                   user=user_type,
                                   appointments=appointments,
                                   today_appointments=today_appointments,
                                   pending_appointments=pending_appointments,
                                   completed_appointments=completed_appointments)
        except Exception as e:
            app.logger.error(f"Receptionist dashboard error: {str(e)}")
            flash('An error occurred while loading the dashboard. Please try again.')
            return redirect(url_for('home'))

    # Create appointment route
    @app.route('/create_appointment/<user_type>', methods=['GET', 'POST'])
    @login_required
    def create_appointment(user_type):
        try:
            if current_user.role != 'receptionist':
                flash('Unauthorized access')
                return redirect(url_for('home'))

            if request.method == 'POST':
                doctor = Doctor.query.get(request.form.get('doctor'))
                patient = Patient.query.get(request.form.get('patient'))

                if not doctor or not patient:
                    flash('Invalid doctor or patient selection')
                    return redirect(url_for('create_appointment', user_type=user_type))

                appointment = Appointment(
                    doctor=doctor,
                    patient=patient,
                    time=request.form.get('time'),
                    date=request.form.get('date'),
                    status=False
                )

                db.session.add(appointment)
                try:
                    db.session.commit()
                    flash('Appointment created successfully')
                    return redirect(url_for('receptionist_dashboard', user_type='R'))
                except Exception as e:
                    db.session.rollback()
                    flash('Failed to create appointment')

            patients = Patient.query.all()
            doctors = Doctor.query.filter_by(status=True).all()  # Only show active doctors
            return render_template('create_appointment.html',
                                   user=user_type,
                                   patient_names=patients,
                                   doctor_names=doctors)
        except Exception as e:
            app.logger.error(f"Create appointment error: {str(e)}")
            flash('An error occurred while processing your request. Please try again.')
            return redirect(url_for('receptionist_dashboard', user_type=user_type))

    # My appointments route
    @app.route('/myappointment')
    @login_required
    def myappointment():
        if current_user.role == 'patient':
            appointments = Appointment.query.filter_by(patient=current_user.patient).all()
            return render_template('my_appointment.html',
                                   data=appointments,
                                   user='P')
        flash('Unauthorized access')
        return redirect(url_for('home'))

    # Doctor appointments route
    @app.route('/doctor_appointment')
    @login_required
    def doctor_appointment():
        if current_user.role == 'doctor':
            appointments = Appointment.query.filter_by(doctor=current_user.doctor).all()
            return render_template('my_appointment.html',
                                   data=appointments,
                                   user='D')
        flash('Unauthorized access')
        return redirect(url_for('home'))

    # Create prescription route
    @app.route('/create_prescription', methods=['GET', 'POST'])
    @login_required
    def create_prescription():
        if current_user.role != 'doctor':
            flash('Unauthorized access')
            return redirect(url_for('home'))

        if request.method == 'POST':
            try:
                appointment = Appointment.query.get(request.form.get('appointment'))
                if not appointment:
                    flash('Invalid appointment selected')
                    return redirect(url_for('create_prescription'))

                prescription = Prescription(
                    symptoms=request.form.get('symptoms'),
                    prescription=request.form.get('prescription'),
                    patient=appointment.patient,
                    doctor=current_user.doctor,
                    appointment=appointment,
                    outstanding=request.form.get('outstanding', 0),
                    paid=request.form.get('paid', 0),
                    total=request.form.get('total', 0)
                )

                db.session.add(prescription)
                try:
                    db.session.commit()
                    flash('Prescription created successfully')
                    return redirect(url_for('doctor_prescription'))
                except Exception as e:
                    db.session.rollback()
                    flash('Failed to create prescription')
                    app.logger.error(f"Prescription creation error: {str(e)}")

            except Exception as e:
                flash('An error occurred while creating the prescription')
                app.logger.error(f"Prescription creation error: {str(e)}")

        appointments = Appointment.query.filter_by(
            doctor=current_user.doctor,
            status=False
        ).all()

        return render_template('create_prescription.html',
                               data=appointments,
                               user='D')

    # Medical history route
    @app.route('/medical_history')
    @login_required
    def medical_history():
        if current_user.role != 'patient':
            flash('Unauthorized access')
            return redirect(url_for('home'))

        prescriptions = Prescription.query.filter_by(patient=current_user.patient).all()
        return render_template('medical_history.html',
                               data=prescriptions,
                               user='P')

    # About route
    @app.route('/about')
    def about():
        return render_template('about.html')

    # HR Dashboard routes
    @app.route('/hr_dashboard')
    @login_required
    def hr_dashboard():
        if current_user.role != 'hr':
            flash('Unauthorized access')
            return redirect(url_for('home'))

        doctors = Doctor.query.all()
        total_doctors = len(doctors)
        active_doctors = len([d for d in doctors if d.status])

        patients = Patient.query.all()
        total_patients = len(patients)

        today = datetime.now().strftime('%Y-%m-%d')
        today_appointments = Appointment.query.filter_by(date=today).count()

        total_outstanding = sum(float(p.invoice.outstanding or 0) for p in patients if p.invoice)
        total_paid = sum(float(p.invoice.paid or 0) for p in patients if p.invoice)

        return render_template('hr_dashboard.html',
                               doctors=doctors,
                               total_doctors=total_doctors,
                               active_doctors=active_doctors,
                               total_patients=total_patients,
                               today_appointments=today_appointments,
                               total_outstanding=total_outstanding,
                               total_paid=total_paid)

    @app.route('/manage_doctors')
    @login_required
    def manage_doctors():
        if current_user.role != 'hr':
            flash('Unauthorized access')
            return redirect(url_for('home'))

        doctors = Doctor.query.all()
        return render_template('manage_doctors.html', doctors=doctors)

    @app.route('/manage_invoices')
    @login_required
    def manage_invoices():
        if current_user.role != 'hr':
            flash('Unauthorized access')
            return redirect(url_for('home'))

        invoices = Invoice.query.all()
        return render_template('manage_invoices.html', invoices=invoices)

    @app.route('/update_invoice/<int:invoice_id>', methods=['POST'])
    @login_required
    def update_invoice(invoice_id):
        if current_user.role != 'hr':
            return {'success': False, 'error': 'Unauthorized'}, 403

        invoice = Invoice.query.get_or_404(invoice_id)
        invoice.outstanding = request.form.get('outstanding', '0')
        invoice.paid = request.form.get('paid', '0')

        try:
            db.session.commit()
            return {'success': True}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}

    @app.route('/update_doctor/<int:doctor_id>', methods=['POST'])
    @login_required
    def update_doctor(doctor_id):
        if current_user.role != 'hr':
            flash('Unauthorized access')
            return redirect(url_for('home'))

        try:
            doctor = Doctor.query.get_or_404(doctor_id)
            doctor.department = request.form.get('department')
            doctor.attendance = int(request.form.get('attendance', 0))
            doctor.salary = int(request.form.get('salary', 0))

            db.session.commit()
            flash('Doctor information updated successfully')
            return redirect(url_for('manage_doctors'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating doctor: {str(e)}")
            flash('Failed to update doctor information')
            return redirect(url_for('manage_doctors'))

    @app.route('/toggle_doctor_status/<int:doctor_id>', methods=['POST'])
    @login_required
    def toggle_doctor_status(doctor_id):
        if current_user.role != 'hr':
            return {'success': False, 'error': 'Unauthorized'}, 403

        try:
            doctor = Doctor.query.get_or_404(doctor_id)
            doctor.status = not doctor.status
            db.session.commit()
            return {'success': True}
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error toggling doctor status: {str(e)}")
            return {'success': False, 'error': str(e)}

    @app.route('/api/doctor/<int:doctor_id>')
    @login_required
    def get_doctor(doctor_id):
        if current_user.role != 'hr':
            return {'error': 'Unauthorized'}, 403

        doctor = Doctor.query.get_or_404(doctor_id)
        return {
            'department': doctor.department,
            'attendance': doctor.attendance,
            'salary': doctor.salary
        }

    @app.route('/send_invoice_email/<int:invoice_id>')
    @login_required
    def send_invoice_email(invoice_id):
        if current_user.role != 'hr':
            flash('Unauthorized access')
            return redirect(url_for('home'))

        invoice = Invoice.query.get_or_404(invoice_id)
        patient = invoice.patient

        # Here you would implement email sending logic
        # For now, we'll just simulate it
        flash(f'Invoice email sent to {patient.email}')
        return redirect(url_for('manage_invoices'))

    @app.route('/generate_invoice_pdf/<int:invoice_id>')
    @login_required
    def generate_invoice_pdf(invoice_id):
        if current_user.role not in ['hr', 'receptionist']:
            flash('Unauthorized access')
            return redirect(url_for('home'))

        invoice = Invoice.query.get_or_404(invoice_id)
        patient = invoice.patient

        # Create HTML content for PDF
        html_content = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .header {{ text-align: center; margin-bottom: 30px; }}
                    .invoice-details {{ margin: 20px 0; }}
                    .total {{ margin-top: 30px; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Health Application Invoice</h1>
                    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>

                <div class="invoice-details">
                    <h2>Patient Information</h2>
                    <p>Name: {patient.name}</p>
                    <p>Email: {patient.email}</p>
                    <p>Phone: {patient.phone}</p>

                    <h2>Invoice Details</h2>
                    <p>Outstanding Amount: ${invoice.outstanding}</p>
                    <p>Paid Amount: ${invoice.paid}</p>
                    <p class="total">Total Amount: ${float(invoice.outstanding) + float(invoice.paid)}</p>
                </div>
            </body>
        </html>
        """

        # Generate PDF
        pdf_path = f'temp_invoice_{invoice_id}.pdf'
        pdfkit.from_string(html_content, pdf_path)

        try:
            return send_file(pdf_path, as_attachment=True, download_name=f'invoice_{invoice_id}.pdf')
        finally:
            # Clean up the temporary file
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

    @app.route('/manage_patients')
    @login_required
    def manage_patients():
        if current_user.role != 'hr':
            flash('Unauthorized access')
            return redirect(url_for('home'))

        patients = Patient.query.all()
        return render_template('manage_patients.html', patients=patients)

    @app.route('/delete_patient/<int:patient_id>', methods=['POST'])
    @login_required
    def delete_patient(patient_id):
        if current_user.role != 'hr':
            flash('Unauthorized access')
            return redirect(url_for('home'))

        try:
            patient = Patient.query.get_or_404(patient_id)
            
            # Delete associated records first
            if patient.invoice:
                db.session.delete(patient.invoice)
            
            # Delete prescriptions
            for prescription in patient.prescriptions:
                db.session.delete(prescription)
            
            # Delete appointments
            for appointment in patient.appointments:
                db.session.delete(appointment)
            
            # Delete the user account
            if patient.user:
                db.session.delete(patient.user)
            
            # Finally delete the patient
            db.session.delete(patient)
            
            try:
                db.session.commit()
                flash(f'Patient {patient.name} has been deleted successfully')
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Database error while deleting patient {patient_id}: {str(e)}")
                flash('Error deleting patient. Please try again.')
                
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error deleting patient {patient_id}: {str(e)}")
            flash('Error deleting patient. Please try again.')
            
        return redirect(url_for('manage_patients'))

    @app.route('/manage_users')
    @login_required
    def manage_users():
        if current_user.role != 'hr':
            flash('Unauthorized access')
            return redirect(url_for('home'))

        users = User.query.all()
        return render_template('manage_users.html', users=users)

    @app.route('/change_password/<int:user_id>', methods=['POST'])
    @login_required
    def change_password(user_id):
        if current_user.role != 'hr':
            flash('Unauthorized access')
            return redirect(url_for('home'))

        try:
            user = User.query.get_or_404(user_id)
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if not new_password or not confirm_password:
                flash('Both password fields are required')
                return redirect(url_for('manage_users'))

            if new_password != confirm_password:
                flash('Passwords do not match')
                return redirect(url_for('manage_users'))

            # Set the new password
            user.set_password(new_password)
            
            try:
                db.session.commit()
                flash(f'Password for {user.username} has been changed successfully')
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Database error while changing password for user {user_id}: {str(e)}")
                flash('Error changing password. Please try again.')
                
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error changing password for user {user_id}: {str(e)}")
            flash('Error changing password. Please try again.')
            
        return redirect(url_for('manage_users'))

    @app.route('/delete_user/<int:user_id>', methods=['POST'])
    @login_required
    def delete_user(user_id):
        if current_user.role != 'hr':
            flash('Unauthorized access')
            return redirect(url_for('home'))

        try:
            user = User.query.get_or_404(user_id)
            
            # Delete associated records based on role
            if user.role == 'patient':
                if user.patient:
                    if user.patient.invoice:
                        db.session.delete(user.patient.invoice)
                    for prescription in user.patient.prescriptions:
                        db.session.delete(prescription)
                    for appointment in user.patient.appointments:
                        db.session.delete(appointment)
                    db.session.delete(user.patient)
            elif user.role == 'doctor':
                if user.doctor:
                    for appointment in user.doctor.appointments:
                        db.session.delete(appointment)
                    for prescription in user.doctor.prescriptions:
                        db.session.delete(prescription)
                    db.session.delete(user.doctor)
            elif user.role == 'receptionist':
                if user.receptionist:
                    db.session.delete(user.receptionist)
            elif user.role == 'hr':
                if user.hr:
                    db.session.delete(user.hr)
            
            # Finally delete the user
            db.session.delete(user)
            
            try:
                db.session.commit()
                flash(f'User {user.username} has been deleted successfully')
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Database error while deleting user {user_id}: {str(e)}")
                flash('Error deleting user. Please try again.')
                
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error deleting user {user_id}: {str(e)}")
            flash('Error deleting user. Please try again.')
            
        return redirect(url_for('manage_users'))

    @app.route('/doctor/order-lab-test', methods=['GET', 'POST'])
    @login_required
    def order_lab_test():
        if current_user.role != 'doctor':
            flash('Access denied')
            return redirect(url_for('home'))
            
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        if not doctor:
            flash('Doctor profile not found')
            return redirect(url_for('home'))
            
        # Get all patients who have appointments with this doctor
        appointments = Appointment.query.filter_by(doctor_id=doctor.id).all()
        
        # Create form and set patient choices
        form = LabTestForm()
        form.patient_id.choices = [(app.patient.id, f"{app.patient.name} ({app.patient.phone})") for app in appointments]
            
        if form.validate_on_submit():
            lab_result = LabResult(
                patient_id=form.patient_id.data,
                doctor_id=doctor.id,
                test_name=form.test_name.data,
                notes=form.notes.data,
                status='ordered'
            )
            
            db.session.add(lab_result)
            db.session.commit()
            flash('Lab test ordered successfully')
            return redirect(url_for('doctor_lab_results'))
            
        # Get ordered results for display
        ordered_results = LabResult.query.filter_by(doctor_id=doctor.id, status='ordered').all()
        return render_template('doctor/order_lab_test.html', form=form, appointments=appointments, ordered_results=ordered_results)

    @app.route('/lab-tech/lab-results', methods=['GET', 'POST'])
    @login_required
    def lab_tech_results():
        if current_user.role != 'lab_tech':
            flash('Access denied')
            return redirect(url_for('home'))
            
        lab_tech = LabTech.query.filter_by(user_id=current_user.id).first()
        if not lab_tech:
            flash('Lab technician profile not found')
            return redirect(url_for('home'))
            
        if request.method == 'POST':
            # Verify CSRF token
            if not request.form.get('csrf_token'):
                flash('CSRF token missing')
                return redirect(url_for('lab_tech_results'))
                
            result_id = request.form.get('result_id')
            if result_id and result_id.isdigit():
                result_id = int(result_id)
                lab_result = LabResult.query.get_or_404(result_id)
                
                # Get form data
                result_value = request.form.get('result_value')
                reference_range = request.form.get('reference_range')
                notes = request.form.get('notes')
                
                if not result_value or not reference_range:
                    flash('Result value and reference range are required')
                    return redirect(url_for('lab_tech_results'))
                
                try:
                    lab_result.result_value = result_value
                    lab_result.reference_range = reference_range
                    lab_result.notes = notes
                    lab_result.result_date = datetime.utcnow()
                    lab_result.status = 'completed'
                    lab_result.lab_tech_id = lab_tech.id
                    
                    # Handle file upload if present
                    if 'result_file' in request.files:
                        file = request.files['result_file']
                        if file and file.filename:
                            filename = secure_filename(file.filename)
                            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'lab_results', filename)
                            os.makedirs(os.path.dirname(file_path), exist_ok=True)
                            file.save(file_path)
                            lab_result.file_path = file_path
                    
                    db.session.commit()
                    flash('Lab result updated successfully')
                except Exception as e:
                    db.session.rollback()
                    app.logger.error(f"Error updating lab result: {str(e)}")
                    flash('Error updating lab result')
            else:
                flash('Invalid result ID')
            return redirect(url_for('lab_tech_results'))
            
        # Get all lab results ordered but not yet processed
        ordered_results = LabResult.query.filter_by(status='ordered').all()
        # Get results being processed by this lab tech
        processing_results = LabResult.query.filter_by(lab_tech_id=lab_tech.id, status='processing').all()
        # Get completed results
        completed_results = LabResult.query.filter_by(lab_tech_id=lab_tech.id, status='completed').all()
        
        return render_template('lab_tech/lab_results.html',
                             ordered_results=ordered_results,
                             processing_results=processing_results,
                             completed_results=completed_results)

    @app.route('/doctor/lab-results', methods=['GET', 'POST'])
    @login_required
    def doctor_lab_results():
        if current_user.role != 'doctor':
            flash('Access denied')
            return redirect(url_for('home'))
            
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        if not doctor:
            flash('Doctor profile not found')
            return redirect(url_for('home'))
            
        if request.method == 'POST':
            result_id = request.form.get('result_id')
            doctor_notes = request.form.get('doctor_notes')
            
            lab_result = LabResult.query.get_or_404(result_id)
            lab_result.doctor_notes = doctor_notes
            lab_result.reviewed_at = datetime.utcnow()
            lab_result.status = 'reviewed'
            
            db.session.commit()
            flash('Lab result reviewed successfully')
            return redirect(url_for('doctor_lab_results'))
            
        # Get all lab results for patients of this doctor
        ordered_results = LabResult.query.filter_by(doctor_id=doctor.id, status='ordered').all()
        completed_results = LabResult.query.filter_by(doctor_id=doctor.id, status='completed').all()
        reviewed_results = LabResult.query.filter_by(doctor_id=doctor.id, status='reviewed').all()
        
        return render_template('doctor/lab_results.html',
                             ordered_results=ordered_results,
                             completed_results=completed_results,
                             reviewed_results=reviewed_results)

    @app.route('/doctor/schedule', methods=['GET', 'POST'])
    @login_required
    def doctor_schedule():
        if current_user.role != 'doctor':
            flash('Access denied')
            return redirect(url_for('home'))
            
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        if not doctor:
            flash('Doctor profile not found')
            return redirect(url_for('home'))
            
        if request.method == 'POST':
            day_of_week = int(request.form.get('day_of_week'))
            start_time = datetime.strptime(request.form.get('start_time'), '%H:%M').time()
            end_time = datetime.strptime(request.form.get('end_time'), '%H:%M').time()
            max_patients = int(request.form.get('max_patients', 10))
            break_start = request.form.get('break_start')
            break_end = request.form.get('break_end')
            
            # Convert break times if provided
            if break_start and break_end:
                break_start = datetime.strptime(break_start, '%H:%M').time()
                break_end = datetime.strptime(break_end, '%H:%M').time()
            
            schedule = DoctorSchedule(
                doctor_id=doctor.id,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
                max_patients=max_patients,
                break_start=break_start,
                break_end=break_end
            )
            
            db.session.add(schedule)
            db.session.commit()
            flash('Schedule updated successfully')
            return redirect(url_for('doctor_schedule'))
            
        schedules = DoctorSchedule.query.filter_by(doctor_id=doctor.id).all()
        return render_template('doctor/schedule.html', schedules=schedules)

    @app.route('/doctor/update-record/<int:patient_id>', methods=['GET', 'POST'])
    @login_required
    def update_patient_record(patient_id):
        if current_user.role != 'doctor':
            flash('Access denied')
            return redirect(url_for('home'))
            
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        if not doctor:
            flash('Doctor profile not found')
            return redirect(url_for('home'))
            
        patient = Patient.query.get_or_404(patient_id)
        
        if request.method == 'POST':
            # Update patient medical information
            patient.medical = request.form.get('medical_history')
            patient.case = request.form.get('case')
            
            # Create new prescription if provided
            prescription_text = request.form.get('prescription')
            symptoms = request.form.get('symptoms')
            
            if prescription_text and symptoms:
                prescription = Prescription(
                    prescription=prescription_text,
                    symptoms=symptoms,
                    patient_id=patient.id,
                    doctor_id=doctor.id,
                    appointment_id=None  # Can be updated if needed
                )
                db.session.add(prescription)
            
            db.session.commit()
            flash('Patient record updated successfully')
            return redirect(url_for('update_patient_record', patient_id=patient_id))
            
        # Get patient's medical history
        prescriptions = Prescription.query.filter_by(patient_id=patient_id).all()
        lab_results = LabResult.query.filter_by(patient_id=patient_id).all()
        
        return render_template('doctor/update_record.html',
                             patient=patient,
                             prescriptions=prescriptions,
                             lab_results=lab_results)

    @app.route('/doctor/view-lab-result/<int:result_id>')
    @login_required
    def view_lab_result(result_id):
        if current_user.role != 'doctor':
            flash('Access denied')
            return redirect(url_for('home'))
            
        lab_result = LabResult.query.get_or_404(result_id)
        return render_template('doctor/view_lab_result.html', lab_result=lab_result)

    @app.route('/doctor/delete-schedule/<int:schedule_id>', methods=['POST'])
    @login_required
    def delete_schedule(schedule_id):
        if current_user.role != 'doctor':
            flash('Access denied')
            return redirect(url_for('home'))
            
        schedule = DoctorSchedule.query.get_or_404(schedule_id)
        db.session.delete(schedule)
        db.session.commit()
        flash('Schedule deleted successfully')
        return redirect(url_for('doctor_schedule'))

    @app.route('/patient/lab-results')
    @login_required
    def patient_lab_results():
        if current_user.role != 'patient':
            flash('Access denied')
            return redirect(url_for('home'))
            
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            flash('Patient profile not found')
            return redirect(url_for('home'))
            
        # Get all lab results for this patient
        lab_results = LabResult.query.filter_by(patient_id=patient.id).order_by(LabResult.test_date.desc()).all()
        
        return render_template('patient/lab_results.html', lab_results=lab_results)
