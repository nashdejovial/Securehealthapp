import os
import sys

# Add your project directory to the sys.path
project_home = '/home/yourusername/SecurehealthApp'
if project_home not in sys.path:
    sys.path.append(project_home)

# Import your Flask app
from wsgi import app as application

# Set environment variables
os.environ['FLASK_ENV'] = 'production' 