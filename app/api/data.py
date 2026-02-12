from flask import Blueprint, request, jsonify, send_file, current_app
from .. import db
from ..models import User, Prediction
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..cost_model import load_models, compute_cost_breakdown, load_unit_costs
from ..blueprint_features import extract_blueprint_features
from ..utils import send_email, generate_pdf
import json
import os
import io
from datetime import datetime
import base64

data_bp = Blueprint('data_api', __name__)

# Load Models (Lazy load or simple global if context allows, but safe inside request or try block)
# To avoid issues, let's load them global but resiliently.
try:
    qty_model, total_cost_model = load_models()
    unit_costs = load_unit_costs()
except Exception as e:
    print(f"Model load error: {e}")
    MODEL_LOAD_ERROR = str(e)
    qty_model = None
    total_cost_model = None
    unit_costs = {}

@data_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    user_id = get_jwt_identity()
    predictions = Prediction.query.filter_by(user_id=user_id).order_by(Prediction.created_at.desc()).all()
    
    data = []
    for p in predictions:
        data.append({
            "id": p.id,
            "date": p.created_at.strftime('%Y-%m-%d'),
            "city": json.loads(p.inputs).get('city', 'Unknown'),
            "total_cost": p.total_cost,
            "predicted_2026": p.predicted_2026_cost
        })
    
    total_value = sum(p.total_cost for p in predictions)
    return jsonify(estimations=data, total_value=total_value, count=len(data)), 200

@data_bp.route('/estimate', methods=['POST'])
@jwt_required()
def estimate():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    print(f"DEBUG: Estimate call from user {user.username} ({user.email})")
    
    # Robust data extraction from either JSON or Form
    if request.is_json:
        form_data = request.get_json()
    else:
        form_data = request.form

    # Check if multipart (file upload)
    if 'blueprint' in request.files and request.files['blueprint'].filename != '':
        f = request.files['blueprint']
        feats = extract_blueprint_features(f.read())
    else:
        # Defaults if no image
        feats = {"area_sqft_estimate": 900, "rooms_estimate": 5, "wall_length_ft": 120}

    # Extract fields
    city = form_data.get('city', 'Chennai')
    # quality names in train_models.py: ['economical', 'standard', 'premium', 'high-end']
    # frontend sends: ['basic', 'standard', 'premium']
    quality = form_data.get('quality', 'standard').lower()
    if quality == 'basic': quality = 'economical' # Map basic to economical for model
    
    try:
        floors = int(form_data.get('floors', 2))
        carpet_ratio = float(form_data.get('carpet_ratio', 0.72))
        is_commercial = form_data.get('is_commercial', False)
        
        # Overrides - handle empty strings safely
        area_override = form_data.get('area_sqft')
        if area_override and area_override != '':
            feats["area_sqft_estimate"] = float(area_override)
            
        rooms_override = form_data.get('rooms')
        if rooms_override and rooms_override != '':
            feats["rooms_estimate"] = int(rooms_override)

        wall_override = form_data.get('wall_length')
        if wall_override and wall_override != '':
            feats["wall_length_ft"] = float(wall_override)
        
        input_data = {
            "city": city,
            "quality": quality,
            "area_sqft": feats["area_sqft_estimate"],
            "no_of_floors": floors,
        }

        if qty_model and total_cost_model:
            # Predict quantities
            q = qty_model.predict(input_data)[0]
            qty_cols = ["bricks_count","cement_bags","steel_kg","paint_liters","worker_days"]
            qty_pred = dict(zip(qty_cols, [int(round(max(0, v))) for v in q]))
            
            cost_res = compute_cost_breakdown(qty_pred, city, quality, unit_costs)
            total_predicted = max(0, total_cost_model.predict_total_cost(input_data)[0])
            
            inflation = current_app.config.get('INFLATION_RATE', 0.07)
            years_diff = 2026 - datetime.now().year
            predicted_2026 = total_predicted * ((1 + inflation) ** max(0, years_diff))

            inputs = {
                "city": city,
                "quality": quality,
                "floors": floors,
                "carpet_ratio": carpet_ratio,
                "is_commercial": is_commercial,
                **feats
            }

            prediction = Prediction(
                inputs=json.dumps(inputs),
                quantities=json.dumps(qty_pred),
                cost_breakdown=json.dumps(cost_res["breakdown"]),
                total_cost=total_predicted,
                predicted_2026_cost=predicted_2026,
                author=user
            )
            db.session.add(prediction)
            db.session.commit()

            # Generate PDF and Email API response
            try:
                pdf_data = {
                    'user': {'name': user.username, 'email': user.email},
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'id': prediction.id,
                    'inputs': inputs,
                    'quantities': qty_pred,
                    'breakdown': cost_res["breakdown"],
                    'total': total_predicted,
                    'predicted_2026': predicted_2026
                }
                pdf_bytes = generate_pdf(pdf_data)
                
                # Send Email
                send_email("Your Estimation Report", user.email,
                           body=f"Hi {user.username},\n\nPlease find attached the detailed cost estimation report.\n\nTotal: Rs. {total_predicted:,.2f}",
                           pdf_bytes=pdf_bytes, pdf_name=f"estimate_{prediction.id}.pdf")
            except Exception as e:
                print(f"PDF/Email Error: {e}")

            return jsonify({
                "id": prediction.id,
                "total_cost": total_predicted,
                "predicted_2026": predicted_2026,
                "quantities": qty_pred,
                "breakdown": cost_res["breakdown"],
                "pdf_generated": True
            }), 201
            
        return jsonify({"msg": f"Models not loaded. Error: {globals().get('MODEL_LOAD_ERROR', 'Unknown')}"}), 500

    except Exception as e:
        print(f"Estimation Logic Error: {e}")
        return jsonify({"msg": f"Internal estimation error: {str(e)}"}), 500

@data_bp.route('/result/<int:pred_id>', methods=['GET'])
@jwt_required()
def result(pred_id):
    user_id = int(get_jwt_identity())
    pred = Prediction.query.filter_by(id=pred_id).first()
    
    if not pred:
        return jsonify({"msg": "Estimation not found"}), 404
        
    if pred.user_id != user_id:
        # Check admin
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return jsonify({"msg": "Unauthorized: You do not own this estimation"}), 403

    return jsonify({
        "inputs": json.loads(pred.inputs),
        "quantities": json.loads(pred.quantities),
        "breakdown": json.loads(pred.cost_breakdown),
        "total_cost": pred.total_cost,
        "predicted_2026": pred.predicted_2026_cost,
        "date": pred.created_at.strftime('%Y-%m-%d')
    }), 200
