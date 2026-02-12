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
import pandas as pd
import json
from datetime import datetime

# Define routes directly on app for simplicity, or use Blueprint if preferring modularity.
# Given the size, defining on app or using a 'main' blueprint is fine.
# Let's use app.route for now as __init__.py didn't set up blueprints yet, or I can update it.
# I'll use app.route to keep it simple as per the __init__ structure I created.

# Load ML models once
try:
    qty_model, total_cost_model = load_models()
    unit_costs = load_unit_costs(os.path.join(app.root_path, 'unit_costs.json'))
except Exception as e:
    print(f"Error loading models: {e}")
    qty_model = None
    total_cost_model = None
    unit_costs = {}

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

