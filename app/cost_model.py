# cost_model.py
import json
import os
from typing import Dict, Any

def load_unit_costs(path=None) -> Dict[str, Any]:
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "unit_costs.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def compute_cost_breakdown(quantities: Dict[str, Any], city: str, quality: str, unit_costs_data: Dict[str, Any]):
    base = unit_costs_data.get('base', {})
    city_mults = unit_costs_data.get('city_multiplier', {})
    qual_mults = unit_costs_data.get('quality_multiplier', {})
    
    # Map 'economical' or 'basic'
    if quality == 'economical': quality = 'basic'
    
    city_mult = city_mults.get(city, 1.0)
    qual_mult = qual_mults.get(quality, 1.0)
    overall_mult = city_mult * qual_mult
    
    breakdown = {}
    
    # Bricks
    bricks_qty = quantities.get('bricks_count', 0) or quantities.get('bricks', 0)
    breakdown['bricks'] = (bricks_qty / 1000) * base.get('brick_per_1000', 6500) * overall_mult
    
    # Cement
    cement_qty = quantities.get('cement_bags', 0) or quantities.get('cement', 0)
    breakdown['cement'] = cement_qty * base.get('cement_bag', 380) * overall_mult
    
    # Steel
    steel_qty = quantities.get('steel_kg', 0) or quantities.get('steel', 0)
    breakdown['steel'] = steel_qty * base.get('steel_kg', 78) * overall_mult
    
    # Paint
    paint_qty = quantities.get('paint_liters', 0) or quantities.get('paint', 0)
    breakdown['paint'] = paint_qty * base.get('paint_liter', 260) * overall_mult
    
    # Labor
    labor_qty = quantities.get('worker_days', 0) or quantities.get('labor', 0)
    breakdown['labor'] = labor_qty * base.get('labor_day', 1000) * overall_mult
    
    total = sum(breakdown.values())
    return {"breakdown": breakdown, "total": total}

class CostEstimatorModel:
    def __init__(self):
        # Material prediction factors (based on training data trends)
        self.material_data = {
            'cement': 0.4,   # bags per sqft
            'steel': 4.0,    # kg per sqft
            'bricks': 8.0,   # nos per sqft
            'sand': 1.8,     # cft per sqft
            'paint': 0.18,   # liters per sqft
            'labor': 0.12    # days per sqft
        }
        
    def predict(self, data: Dict[str, Any]):
        """
        Pure Python implementation of material quantity prediction.
        data: dictionary containing 'area_sqft'
        """
        if isinstance(data, list) and len(data) > 0:
            area = data[0].get('area_sqft', 0)
        else:
            area = data.get('area_sqft', 0)
            
        # Calculate quantities based on factors
        res = [
            area * self.material_data['bricks'],
            area * self.material_data['cement'],
            area * self.material_data['steel'],
            area * self.material_data['paint'],
            area * self.material_data['labor']
        ]
        return [res]

    def predict_total_cost(self, data: Dict[str, Any]):
        """
        Pure Python implementation of total cost prediction.
        Now uses consolidated multipliers from unit_costs.json via compute_cost_breakdown.
        """
        if isinstance(data, list) and len(data) > 0:
            item = data[0]
        elif hasattr(data, 'iloc'):
            item = data.iloc[0].to_dict()
        else:
            item = data

        city = item.get('city', 'Chennai')
        quality = item.get('quality', 'standard')
        area = item.get('area_sqft', 0)
        floors = item.get('no_of_floors', 1)
        
        # Get quantities
        q_raw = self.predict(item)[0]
        q_dict = {
            "bricks_count": q_raw[0],
            "cement_bags": q_raw[1],
            "steel_kg": q_raw[2],
            "paint_liters": q_raw[3],
            "worker_days": q_raw[4]
        }
        
        # Load unit costs (local load for robustness)
        try:
            u_costs = load_unit_costs()
        except:
            u_costs = {}
            
        # Get breakdown total
        res = compute_cost_breakdown(q_dict, city, quality, u_costs)
        
        # Multiply by floors (assuming base area is per floor or total area is passed)
        # In this app, area is usually total area, so floors might be a multiplier for height-related complexity
        # if the training data suggests so. If area is per floor, we multiply by floors.
        # Let's assume area is per floor based on previous logic: area * floors * base_rate
        total_cost = res["total"] * floors
        
        return [total_cost]

def load_models():
    """Returns a mockable interface to keep existing code working."""
    model = CostEstimatorModel()
    return model, model
