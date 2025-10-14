import pytest
import os
import tempfile
from app import create_app, db
from app.models import LandParcel, User
from config import TestingConfig

class TestConfig(TestingConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def init_database(app):
    """Initialize database with test data."""
    with app.app_context():
        # Add test user
        user = User(email='test@example.com', name='Test User')
        user.set_password('password123')
        db.session.add(user)

        # Add test parcels
        parcels = [
            LandParcel(name='Test Farm A', location='Test Location',
                      soil_quality=8, vegetation_cover=7, user_id=1),
            LandParcel(name='Test Farm B', location='Test Location',
                      soil_quality=4, vegetation_cover=3, user_id=1)
        ]
        for parcel in parcels:
            parcel.health_score = LandParcel.calculate_health_score(parcel.soil_quality, parcel.vegetation_cover)
            parcel.risk_level, parcel.risk_label, parcel.risk_color = LandParcel.get_risk_category(parcel.health_score)
            db.session.add(parcel)

        db.session.commit()
    return db