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
├── app.py
├── config.py
├── models.py
├── routes.py
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/
├── templates/
│   ├── base.html
│   ├── home.html
│   └── ...
└── requirements.txt
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.





