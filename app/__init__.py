from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config
from flask_mail import Mail

from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Serve React App
import os

app = Flask(__name__, 
            static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../client/dist')))
app.config.from_object(Config)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
jwt = JWTManager(app)
CORS(app) # Enable CORS for all routes

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@app.context_processor
def inject_now():
    from datetime import datetime
    return {'now': datetime.utcnow()}

# Avoid circular imports by importing inside function or after app is ready
from .api.auth import auth_bp
from .api.data import data_bp
from .api.admin import admin_bp
from .routes import main_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(data_bp, url_prefix='/api/data')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(main_bp)

# Ensure database exists
try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print(f"DB Creation Warning: {e}")
