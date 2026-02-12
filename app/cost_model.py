# cost_model.py
import json
import os
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
import joblib

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

def load_unit_costs(path=None) -> Dict[str, Any]:
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "unit_costs.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_dataset(path=None) -> pd.DataFrame:
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "data", "building_cost_dataset.csv")
    df = pd.read_csv(path)
    # basic sanity
    df = df.dropna().reset_index(drop=True)
    return df

class QuantityModel:
    def __init__(self):
        self.models = {}
        self.materials = ['bricks', 'cement', 'steel', 'sand']
        for mat in self.materials:
            path = os.path.join(MODEL_DIR, f"{mat}_model.pkl")
            if os.path.exists(path):
                self.models[mat] = joblib.load(path)
            else:
                self.models[mat] = None

    def predict(self, X):
        # X is a DataFrame. We need area_sqft for predictions.
        # Ensure input columns match what models expect?
        # The simple linear models from training script only used 'area_sqft'.
        
        area = X['area_sqft'].values
        preds = {}
        
        for mat in self.materials:
            if self.models[mat]:
                # Simple models expect just area in some cases, or passed full X 
                # but let's try passing full X if they were trained with it, 
                # OR just area if trained with just area.
                # Training script: X_mat = df[['area_sqft']]
                # So we must pass just DataFrame with area_sqft
                preds[mat] = self.models[mat].predict(X[['area_sqft']])
            else:
                preds[mat] = area * 0 # Fallback
        
        # Heuristics for missing models
        # Paint: approx 0.18 liters per sqft
        paint = area * 0.18
        # Labor: approx 0.12 days per sqft
        labor = area * 0.12
        
        # Order: bricks, cement, steel, paint, labor
        # Make sure to return shape (n_samples, 5)
        # Assuming batch size of 1 usually
        results = []
        for i in range(len(area)):
            results.append([
                preds['bricks'][i],
                preds['cement'][i],
                preds['steel'][i],
                paint[i],
                labor[i]
            ])
        return results

def load_models():
    """Load the retrained models."""
    try:
        qty_model = QuantityModel()
        
        cost_path = os.path.join(MODEL_DIR, "cost_estimator.pkl")
        if os.path.exists(cost_path):
            cost_model = joblib.load(cost_path)
        else:
            cost_model = None
            
        return qty_model, cost_model
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        return None, None

def compute_cost_breakdown(qty_pred: Dict[str,float], city: str, quality: str, unit_cfg: Dict[str,Any]) -> Dict[str, Any]:
    base = unit_cfg["base"]
    cm = unit_cfg["city_multiplier"].get(city, 1.0)
    qm = unit_cfg["quality_multiplier"].get(quality, 1.0)

    mul = cm * qm
    rates = {
        "brick_per_1000": base["brick_per_1000"] * mul,
        "cement_bag": base["cement_bag"] * mul,
        "steel_kg": base["steel_kg"] * mul,
        "paint_liter": base["paint_liter"] * mul,
        "labor_day": base["labor_day"] * mul
    }

    cost_bricks = (qty_pred["bricks_count"]/1000.0) * rates["brick_per_1000"]
    cost_cement = qty_pred["cement_bags"] * rates["cement_bag"]
    cost_steel  = qty_pred["steel_kg"] * rates["steel_kg"]
    cost_paint  = qty_pred["paint_liters"] * rates["paint_liter"]
    cost_labor  = qty_pred["worker_days"] * rates["labor_day"]

    total = cost_bricks + cost_cement + cost_steel + cost_paint + cost_labor

    return {
        "rates": rates,
        "breakdown": {
            "bricks": round(cost_bricks,2),
            "cement": round(cost_cement,2),
            "steel": round(cost_steel,2),
            "paint": round(cost_paint,2),
            "labor": round(cost_labor,2)
        },
        "total": round(total,2)
    }
