import os
import sys

# Add the current directory to the path so we can import 'app'
sys.path.append(os.getcwd())

try:
    from app import app, db
    from app.models import User, Material, Estimation, Prediction
    
    with app.app_context():
        print("Deleting all records...")
        
        # Delete in order to satisfy foreign key constraints if any
        num_predictions = Prediction.query.delete()
        num_estimations = Estimation.query.delete()
        num_materials = Material.query.delete()
        num_users = User.query.delete()
        
        db.session.commit()
        
        print(f"Deleted {num_predictions} Predictions")
        print(f"Deleted {num_estimations} Estimations")
        print(f"Deleted {num_materials} Materials")
        print(f"Deleted {num_users} Users")
        print("\nAll records deleted successfully.")
        
except Exception as e:
    print(f"Error: {e}")
    db.session.rollback()
