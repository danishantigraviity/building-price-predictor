import os
import sys

# Add the current directory to the path so we can import 'app'
sys.path.append(os.getcwd())

try:
    from app import app, db, bcrypt
    from app.models import User
    
    with app.app_context():
        # Check if user exists
        user = User.query.filter_by(email='danish210303@gmail.com').first()
        password = "Password123!"
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        if user:
            print(f"Updating password for existing user: {user.email}")
            user.password = hashed_password
        else:
            print(f"Creating new user: danish210303@gmail.com")
            user = User(username='danish21', email='danish210303@gmail.com', password=hashed_password)
            db.session.add(user)
            
        db.session.commit()
        print("\nSuccess!")
        print(f"Email: danish210303@gmail.com")
        print(f"Password: {password}")
        
except Exception as e:
    print(f"Error: {e}")
