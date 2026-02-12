import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

# Create dummy data for training (simulating the original dataset)
# This is necessary because we don't have the original CSV, 
# but we know the structure from the cost_model.py usage.

print("🚀 Generating synthetic training data...")

cities = ['Chennai', 'Bangalore', 'Coimbatore', 'Mumbai', 'Delhi']
qualities = ['economical', 'standard', 'premium', 'high-end']

data = []
for _ in range(1000):
    city = np.random.choice(cities)
    quality = np.random.choice(qualities)
    area = np.random.randint(500, 5000)
    floors = np.random.randint(1, 5)
    
    # Base cost logic (approximate)
    base_rate = 1500
    if city == 'Mumbai': base_rate *= 1.8
    elif city == 'Delhi': base_rate *= 1.5
    elif city == 'Bangalore': base_rate *= 1.4
    elif city == 'Chennai': base_rate *= 1.2
    
    if quality == 'standard': base_rate *= 1.2
    elif quality == 'premium': base_rate *= 1.5
    elif quality == 'high-end': base_rate *= 2.0
    
    cost = area * floors * base_rate * np.random.uniform(0.9, 1.1)
    
    data.append({
        'city': city,
        'quality': quality,
        'area_sqft': area,
        'no_of_floors': floors,
        'estimated_cost': cost
    })

df = pd.DataFrame(data)

# Features and Target
X = df[['city', 'quality', 'area_sqft', 'no_of_floors']]
y = df['estimated_cost']

# Preprocessing
numeric_features = ['area_sqft', 'no_of_floors']
categorical_features = ['city', 'quality']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

# Model Pipeline
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', GradientBoostingRegressor(n_estimators=100, random_state=42))
])

# Train
print("🧠 Training model...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model.fit(X_train, y_train)

# Evaluate
score = model.score(X_test, y_test)
print(f"✅ Model R2 Score: {score:.4f}")

# Save
model_path = os.path.join('app', 'models', 'cost_estimator.pkl')
os.makedirs(os.path.dirname(model_path), exist_ok=True)
joblib.dump(model, model_path)
print(f"💾 Model saved to {model_path}")

# Material Prediction Models (Simple Linear Regression for demo)
print("🧱 Training material models...")
materials = ['cement', 'steel', 'bricks', 'sand']
material_data = {
    'cement': {'factor': 0.4, 'unit': 'bags'},
    'steel': {'factor': 4.0, 'unit': 'kg'},
    'bricks': {'factor': 8.0, 'unit': 'nos'},
    'sand': {'factor': 1.8, 'unit': 'cft'}
}

for mat in materials:
    X_mat = df[['area_sqft']]
    y_mat = df['area_sqft'] * material_data[mat]['factor'] * np.random.uniform(0.95, 1.05, 1000)
    
    mat_model = LinearRegression()
    mat_model.fit(X_mat, y_mat)
    
    mat_model_path = os.path.join('app', 'models', f'{mat}_model.pkl')
    joblib.dump(mat_model, mat_model_path)
    print(f"  - Saved {mat}_model.pkl")

print("🎉 All models retrained successfully!")
