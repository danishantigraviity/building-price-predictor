# Civil Material Estimator & Price Predictor

A Flask-based web application for estimating construction material quantities and predicting future costs (2026) using Machine Learning.

## Features
- **User Authentication**: Secure Login/Register with password hashing.
- **Material Estimation**: Calculate Cement, Steel, Bricks, Sand, Aggregate based on building specs.
- **Price Prediction**: Real-time cost calculation and 2026 inflation-adjusted forecasts.
- **Dashboard**: Track your previous estimations.
- **Admin Panel**: Manage users and view global activity.
- **Blueprints**: Upload blueprint images to auto-extract features (Area, Rooms, Walls).

## Installation

1. **Clone/Download** the repository.
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configuration**:
   - The app uses `sqlite:///site.db` by default.
   - For MySQL, set `DATABASE_URL` in `.env` or environment variables.
   - `SECRET_KEY` should be set for production.

4. **Run the Application**:
   ```bash
   python run.py
   ```
   The app will run at `http://127.0.0.1:5000`.

## Project Structure
- `app/`: Main application package.
  - `models.py`: Database models.
  - `routes.py`: Logic and endpoints.
  - `templates/`: HTML templates (Bootstrap 5).
  - `static/`: Static assets.
  - `utils.py` / `cost_model.py`: ML logic.
- `run.py`: Entry point.
- `config.py`: Configuration settings.

## Machine Learning
The app uses pre-trained `joblib` models stored in `app/models/` to predict quantities and costs.
