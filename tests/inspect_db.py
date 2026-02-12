from app import app, db
from app.models import Prediction, User
import json

with app.app_context():
    print("--- Users ---")
    users = User.query.all()
    for u in users:
        print(f"ID: {u.id}, Username: {u.username}, Admin: {u.is_admin}")
    
    print("\n--- Recent Predictions ---")
    preds = Prediction.query.order_by(Prediction.id.desc()).limit(10).all()
    for p in preds:
        try:
            inputs = json.loads(p.inputs)
            city = inputs.get('city', 'Unknown')
        except:
            city = 'JSON Error'
        print(f"ID: {p.id}, UserID: {p.user_id}, Total: {p.total_cost}, City: {city}, Created: {p.created_at}")
