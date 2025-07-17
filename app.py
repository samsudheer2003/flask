import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv
from datetime import timedelta
import logging

# Load environment variables
load_dotenv()

# Initialize Flask App
app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///users.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)

# Import extensions and initialize
from extensions import db, jwt, migrate
db.init_app(app)
jwt.init_app(app)

# ✅ Import models BEFORE initializing Migrate
from models import *  # Ensure all models are imported here

migrate = Migrate(app, db)
jwt = JWTManager(app)

# Register Blueprints
from routes.user_router import user_router
from routes.todo_router import todo_router

app.register_blueprint(user_router, url_prefix='/api/users')
app.register_blueprint(todo_router, url_prefix='/api/todos')

# Middleware: Header Validation
@app.before_request
def validate_mandatory_headers():
    if request.endpoint in ('static',):
        return  # Skip static files

    required_headers = ['Content-Type', 'Device-Name', 'Device-Uuid']
    for header in required_headers:
        if header not in request.headers:
            return jsonify({'message': f'Missing required header: {header}'}), 400

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Optional: Twilio Email/SMS Notification Initialization
# from utils.twilio_utils import init_twilio
# init_twilio()

# Root route
@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the TODO API with JWT & Refresh Tokens'}), 200

if __name__ == '__main__':
    app.run(debug=True)
