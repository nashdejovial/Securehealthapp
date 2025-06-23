# Health Application

Welcome to the Health Application repository! This project is built using HTML, CSS, JavaScript, and Flask framework.

## Overview

Health Application is a comprehensive application designed to efficiently manage health-related operations. It covers various aspects of health management, including patient and doctor records, appointments, prescriptions, receptionist tasks, HR functions, and more.

## Features

- User Authentication (Login/Register)
- Role-based Access Control
- Patient Management
- Doctor Management
- Appointment Scheduling
- Prescription Management
- Medical History Tracking
- Invoice Generation
- HR Management
- Responsive Design

## Tech Stack

- Frontend: HTML, CSS, JavaScript, Bootstrap
- Backend: Python Flask
- Database: PostgreSQL
- Authentication: Flask-Login
- Forms: Flask-WTF
- ORM: SQLAlchemy

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/health-application.git
cd health-application
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables:
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
export DATABASE_URL=postgresql://username:password@localhost:5432/health_system
```

5. Initialize database:
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Run the application:
```bash
flask run
```

## Project Structure
```
health-application/
├── app.py                      # Main application file
├── config.py                   # Configuration settings
├── models.py                   # Database models and schemas
├── routes.py                   # URL routes and view functions
├── forms.py                    # Form definitions
├── extensions.py              # Flask extensions initialization
├── __init__.py                # Application factory
├── wsgi.py                    # WSGI application entry point
├── pa_wsgi.py                # PythonAnywhere WSGI configuration
├── cli.py                     # CLI commands
├── manage.py                  # Management script
│
├── static/                    # Static assets
│   ├── css/                  # Stylesheets
│   │   └── style.css        # Main stylesheet
│   ├── js/                  # JavaScript files
│   │   └── main.js         # Main JavaScript
│   └── images/              # Image assets
│
├── templates/                 # Jinja2 HTML templates
│   ├── base.html             # Base template
│   ├── home.html             # Homepage
│   ├── login.html            # Login page
│   ├── register.html         # Registration page
│   ├── about.html            # About page
│   ├── patient/              # Patient-related templates
│   │   ├── dashboard.html
│   │   ├── appointments.html
│   │   └── medical_history.html
│   ├── doctor/               # Doctor-related templates
│   │   ├── dashboard.html
│   │   ├── prescriptions.html
│   │   └── patients.html
│   ├── receptionist/         # Receptionist-related templates
│   │   ├── dashboard.html
│   │   └── appointments.html
│   ├── hr/                   # HR-related templates
│   │   ├── dashboard.html
│   │   └── staff.html
│   └── errors/               # Error templates
│       ├── 404.html
│       └── 500.html
│
├── migrations/               # Database migrations
│   ├── versions/
│   ├── alembic.ini
│   ├── env.py
│   └── script.py.mako
│
├── instance/                # Instance-specific files
│   └── config.py           # Instance configuration
│
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_models.py
│   └── test_routes.py
│
├── media/                   # Media file storage
│   └── uploads/            # User uploads
│
├── requirements.txt         # Python dependencies
├── .env                    # Environment variables (not in git)
├── .gitignore             # Git ignore file
└── README.md              # Project documentation
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.





