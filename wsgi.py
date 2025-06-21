<<<<<<< HEAD
from . import create_app
=======
import os
import sys

# Add the application directory to the Python path
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)

from app import app
>>>>>>> dbe3c0dfb6c7aaeb9eee58f794b33f777104291c

application = create_app()