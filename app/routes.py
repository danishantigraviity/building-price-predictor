import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from . import app, db, bcrypt
from .forms import RegistrationForm, LoginForm, EstimationForm, UpdateAccountForm
from .models import User, Estimation, Prediction
from flask_login import login_user, current_user, logout_user, login_required
from .cost_model import load_models, compute_cost_breakdown, load_unit_costs
from .blueprint_features import extract_blueprint_features
from .utils import send_email, generate_pdf
import json
from datetime import datetime

# Define routes directly on app for simplicity, or use Blueprint if preferring modularity.
# Given the size, defining on app or using a 'main' blueprint is fine.
# Let's use app.route for now as __init__.py didn't set up blueprints yet, or I can update it.
# I'll use app.route to keep it simple as per the __init__ structure I created.

# Deferred loading of models to avoid crashes during initialization
_QTY_MODEL = None
_TOTAL_COST_MODEL = None
_UNIT_COSTS = None

def get_models():
    global _QTY_MODEL, _TOTAL_COST_MODEL, _UNIT_COSTS
    if _QTY_MODEL is None or _TOTAL_COST_MODEL is None:
        try:
            _QTY_MODEL, _TOTAL_COST_MODEL = load_models()
        except Exception as e:
            print(f"Error loading models: {e}")
    return _QTY_MODEL, _TOTAL_COST_MODEL

def get_unit_costs():
    global _UNIT_COSTS
    if _UNIT_COSTS is None:
        try:
            # Look for unit_costs.json in app root path
            path = os.path.join(os.path.dirname(__file__), 'unit_costs.json')
            _UNIT_COSTS = load_unit_costs(path)
        except Exception as e:
            print(f"Error loading unit costs: {e}")
            _UNIT_COSTS = {}
    return _UNIT_COSTS

from flask import send_from_directory

@app.route("/", defaults={'path': ''})
@app.route("/<path:path>")
def serve(path):
    if path.startswith("api"):
         return abort(404)

    # Let Flask's static handler handle files first.
    # If the path exists in static_folder, Flask usually handles it via /static_url_path.
    # But since we set static_url_path='/', it might conflict with this route.
    # However, defined routes take precedence.
    
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
        
    return send_from_directory(app.static_folder, 'index.html')

