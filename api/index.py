import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from app import app
except Exception as e:
    import traceback
    from flask import Flask, jsonify
    
    # Emergency app to report the error
    error_app = Flask(__name__)
    
    @error_app.route('/', defaults={'path': ''})
    @error_app.route('/<path:path>')
    def report_error(path):
        return jsonify({
            "status": "error",
            "error_type": type(e).__name__,
            "message": str(e),
            "traceback": traceback.format_exc(),
            "cwd": os.getcwd(),
            "sys_path": sys.path
        }), 500
    
    app = error_app
