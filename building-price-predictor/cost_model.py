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

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

def load_unit_costs(path="unit_costs.json") -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_dataset(path="data/building_cost_dataset.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    # basic sanity
    df = df.dropna().reset_index(drop=True)
    return df

def train_models(dataset_path="data/building_cost_dataset.csv") -> Tuple[Pipeline, Pipeline]:
    """
    Train two models:
      1) Quantities model → predicts [bricks_count, cement_bags, steel_kg, paint_liters, worker_days]
      2) Total cost model → predicts total_cost directly (backstop)
    """
    df = load_dataset(dataset_path)

    feature_cols = ["city","quality","floors","rooms","area_sqft","wall_length_ft","carpet_ratio"]
    target_qty = ["bricks_count","cement_bags","steel_kg","paint_liters","worker_days"]
    target_cost = "total_cost"

    X = df[feature_cols]
    y_qty = df[target_qty]
    y_cost = df[target_cost]

    numeric = ["floors","rooms","area_sqft","wall_length_ft","carpet_ratio"]
    categorical = ["city","quality"]

    pre = ColumnTransformer([
        ("num", StandardScaler(), numeric),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical)
    ])

    qty_model = Pipeline([
        ("pre", pre),
        ("rf", RandomForestRegressor(n_estimators=220, random_state=42))
    ])

    cost_model = Pipeline([
        ("pre", pre),
        ("rf", RandomForestRegressor(n_estimators=220, random_state=42))
    ])

    X_train, X_test, yq_train, yq_test = train_test_split(X, y_qty, test_size=0.2, random_state=42)
    qty_model.fit(X_train, yq_train)

    Xc_train, Xc_test, yc_train, yc_test = train_test_split(X, y_cost, test_size=0.2, random_state=42)
    cost_model.fit(Xc_train, yc_train)

    joblib.dump(qty_model, os.path.join(MODEL_DIR, "qty_model.joblib"))
    joblib.dump(cost_model, os.path.join(MODEL_DIR, "cost_model.joblib"))

    return qty_model, cost_model

def load_models():
    from pathlib import Path
    qty_path = Path(MODEL_DIR) / "qty_model.joblib"
    cost_path = Path(MODEL_DIR) / "cost_model.joblib"
    if qty_path.exists() and cost_path.exists():
        import joblib
        return joblib.load(qty_path), joblib.load(cost_path)
    return train_models()

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
