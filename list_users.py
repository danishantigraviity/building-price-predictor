import os
import sys

# Add the current directory to the path so we can import 'app'
sys.path.append(os.getcwd())

try:
    from app import app, db
    from app.models import User
    
    with app.app_context():
        users = User.query.all()
        if not users:
            print("No users found in the database.")
        else:
            print("Current users:")
            for u in users:
                print(f"Username: {u.username}, Email: {u.email}")
except Exception as e:
    print(f"Error: {e}")
