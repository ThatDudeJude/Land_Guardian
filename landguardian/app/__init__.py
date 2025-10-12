import os
from dotenv import load_dotenv

from flask import Flask, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from datetime import timedelta

from config import Config

# Load environment variables from .env file
load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
from app import models
models.db = db
models._define_models()

def create_app(config_class=Config):
    """
    Application factory function for creating Flask app instances.

    This function implements the Flask application factory pattern, allowing
    for multiple app instances with different configurations, which is useful
    for testing and running different environments.

    Args:
        config_class: Configuration class to use for the app (default: Config).

    Returns:
        Flask app instance configured with the specified config class.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.remember_cookie_duration = timedelta(days=30)
    login_manager.session_protection = 'strong'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    def init_db():
        """
        Initialize the database with tables and mock data.
        """
        with app.app_context():
            db.create_all()
            from app.models import LandParcel
            from app.models import User
            import random
            from datetime import datetime, timedelta

            if User.query.count() == 0:
                # Create users
                users_data = [
                    {'email': 'john@greenvalleyfarms.com', 'name': 'John Farmer', 'organization': 'Green Valley Farms', 'role': 'farmer'},
                    {'email': 'maria@sunriseorganics.com', 'name': 'Maria Garcia', 'organization': 'Sunrise Organics', 'role': 'farmer'},
                    {'email': 'dchen@agriresearch.edu', 'name': 'David Chen', 'organization': 'State Agricultural University', 'role': 'researcher'},
                    {'email': 'swilson@env.gov', 'name': 'Sarah Wilson', 'organization': 'Environmental Protection Agency', 'role': 'policymaker'}
                ]

                users = []
                for user_data in users_data:
                    user = User(
                        email=user_data['email'],
                        name=user_data['name'],
                        organization=user_data['organization'],
                        role=user_data['role']
                    )
                    user.set_password('password123')  # Default password for testing
                    db.session.add(user)
                    users.append(user)
                db.session.commit()

            if LandParcel.query.count() == 0:
                users = User.query.all()
                # Create parcels distributed among users
                parcels_data = [
                    # Central Valley, CA (3 parcels) - John (0)
                    {'name': 'North Field', 'location': 'Central Valley', 'lat': 36.7783, 'lng': -119.4179, 'soil': 8, 'veg': 7, 'user_idx': 0},
                    {'name': 'River Bottom', 'location': 'Central Valley', 'lat': 36.7378, 'lng': -119.7871, 'soil': 7, 'veg': 6, 'user_idx': 0},
                    # Corn Belt, IA (4 parcels) - Maria (1)
                    {'name': 'South Pasture', 'location': 'Corn Belt', 'lat': 41.8781, 'lng': -93.0977, 'soil': 6, 'veg': 5, 'user_idx': 1},
                    {'name': 'West Meadow', 'location': 'Corn Belt', 'lat': 41.6005, 'lng': -93.6091, 'soil': 7, 'veg': 6, 'user_idx': 1},
                    {'name': 'Hilltop Field', 'location': 'Corn Belt', 'lat': 41.8780, 'lng': -93.0977, 'soil': 5, 'veg': 4, 'user_idx': 1},
                    {'name': 'Valley Plot', 'location': 'Corn Belt', 'lat': 41.6611, 'lng': -91.5302, 'soil': 8, 'veg': 7, 'user_idx': 1},
                    # Texas Panhandle (3 parcels) - John (0), David (2)
                    {'name': 'High Plains', 'location': 'Texas Panhandle', 'lat': 35.2220, 'lng': -101.8313, 'soil': 4, 'veg': 3, 'user_idx': 0},
                    {'name': 'Canyon Lands', 'location': 'Texas Panhandle', 'lat': 34.9829, 'lng': -101.9187, 'soil': 5, 'veg': 4, 'user_idx': 0},
                    {'name': 'Prairie Section', 'location': 'Texas Panhandle', 'lat': 35.4676, 'lng': -100.9059, 'soil': 6, 'veg': 5, 'user_idx': 2},
                    # Mixed regions (5 parcels) - Maria (1), David (2), Sarah (3)
                    {'name': 'Mountain View', 'location': 'Rocky Mountains', 'lat': 39.5501, 'lng': -105.7821, 'soil': 7, 'veg': 6, 'user_idx': 2},
                    {'name': 'Coastal Plain', 'location': 'Gulf Coast', 'lat': 30.4518, 'lng': -91.1871, 'soil': 8, 'veg': 7, 'user_idx': 0},
                    {'name': 'Desert Oasis', 'location': 'Southwest Desert', 'lat': 32.2217, 'lng': -110.9265, 'soil': 3, 'veg': 2, 'user_idx': 0},
                    {'name': 'Lake District', 'location': 'Great Lakes', 'lat': 43.0389, 'lng': -87.9065, 'soil': 9, 'veg': 8, 'user_idx': 1},
                    {'name': 'Forest Grove', 'location': 'Pacific Northwest', 'lat': 47.6062, 'lng': -122.3321, 'soil': 6, 'veg': 5, 'user_idx': 3}
                ]

                for parcel_data in parcels_data:
                    health_score = LandParcel.calculate_health_score(parcel_data['soil'], parcel_data['veg'])
                    risk_level, risk_label, risk_color = LandParcel.get_risk_category(health_score)

                    # Random date within last 3 months
                    days_ago = random.randint(0, 90)
                    last_updated = datetime.utcnow() - timedelta(days=days_ago)

                    parcel = LandParcel(
                        name=parcel_data['name'],
                        location=parcel_data['location'],
                        latitude=parcel_data['lat'],
                        longitude=parcel_data['lng'],
                        soil_quality=parcel_data['soil'],
                        vegetation_cover=parcel_data['veg'],
                        health_score=health_score,
                        risk_level=risk_level,
                        risk_label=risk_label,
                        risk_color=risk_color,
                        user_id=users[parcel_data['user_idx']].id,
                        last_updated=last_updated
                    )
                    db.session.add(parcel)
                db.session.commit()

    init_db()

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; script-src 'self' https://cdn.jsdelivr.net https://unpkg.com; img-src 'self' data: https:; font-src 'self' https://cdn.jsdelivr.net;"
        return response

    return app