import sys
import os

# Add the project directory to the sys.path
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import the Flask app
from app import app as application

# If you are using a virtualenv, PythonAnywhere handles it via their Web tab.
# No need to manually activate it here unless you have a non-standard setup.
