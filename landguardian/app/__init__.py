from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
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
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    def init_db():
        """
        Initialize the database with tables and sample data.
        """
        with app.app_context():
            db.create_all()
            from app.models import LandParcel
            if LandParcel.query.count() == 0:
                samples = [
                    {
                        'name': 'North Farm Field A',
                        'location': 'North Farm',
                        'latitude': 37.7749,
                        'longitude': -122.4194,
                        'soil_quality': 8,
                        'vegetation_cover': 7
                    },
                    {
                        'name': 'South Valley Plot',
                        'location': 'South Valley',
                        'latitude': 37.7510,
                        'longitude': -122.4180,
                        'soil_quality': 4,
                        'vegetation_cover': 3
                    },
                    {
                        'name': 'East Hills Section',
                        'location': 'East Hills',
                        'latitude': 37.7850,
                        'longitude': -122.4100,
                        'soil_quality': 6,
                        'vegetation_cover': 5
                    }
                ]
                for data in samples:
                    health_score = LandParcel.calculate_health_score(data['soil_quality'], data['vegetation_cover'])
                    risk_level, risk_label, risk_color = LandParcel.get_risk_category(health_score)
                    parcel = LandParcel(
                        name=data['name'],
                        location=data['location'],
                        latitude=data['latitude'],
                        longitude=data['longitude'],
                        soil_quality=data['soil_quality'],
                        vegetation_cover=data['vegetation_cover'],
                        health_score=health_score,
                        risk_level=risk_level,
                        risk_label=risk_label,
                        risk_color=risk_color
                    )
                    db.session.add(parcel)
                db.session.commit()

    init_db()

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app