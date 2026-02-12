# cost_model.py
import json
import os
from typing import Dict, Any

def load_unit_costs(path=None) -> Dict[str, Any]:
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "unit_costs.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

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
        data: dictionary containing 'city', 'quality', 'area_sqft', 'no_of_floors'
        """
        # Compatibility handling
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
        
        base_rate = 1500
        # City multiplier logic from training
        city_map = {
            'Mumbai': 1.8,
            'Delhi': 1.5,
            'Bangalore': 1.4,
            'Chennai': 1.2
        }
        base_rate *= city_map.get(city, 1.0)
        
        # Quality multiplier logic from training
        quality_map = {
            'economical': 1.0, # mapping 'economical'
            'standard': 1.2,
            'premium': 1.5,
            'high-end': 2.0
        }
        base_rate *= quality_map.get(quality, 1.0)
        
        cost = area * floors * base_rate
        return [cost]

def load_models():
    """Returns a mockable interface to keep existing code working."""
    model = CostEstimatorModel()
    return model, model
