from flask import Flask, jsonify
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.doctor_routes import doctor_bp
from routes.appointment_routes import appointment_bp
from routes.admin_routes import admin_bp
from config.db import client

app = Flask(__name__)
CORS(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(appointment_bp)
app.register_blueprint(admin_bp)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Quick connectivity test."""
    try:
        # Try a lightweight ping to MongoDB
        client.admin.command('ping')
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected ({str(e)[:80]})"
        
    return jsonify({
        "status": "ok",
        "api": "MedicPulse Flask Backend is running",
        "database": db_status
    }), 200

@app.route('/', methods=['GET'])
def root():
    return jsonify({"message": "MedicPulse Flask API is running. Visit /api/health to check DB status."}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
