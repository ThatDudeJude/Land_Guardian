import pytest
from app.models import LandParcel, User
from app import db

class TestModels:
    def test_user_creation(self, init_database):
        """Test user model creation and password hashing."""
        user = User.query.first()
        assert user.email == 'test@example.com'
        assert user.name == 'Test User'
        assert user.check_password('password123') is True
        assert user.check_password('wrongpassword') is False

    def test_land_parcel_creation(self, init_database):
        """Test land parcel model creation and health scoring."""
        parcels = LandParcel.query.all()
        assert len(parcels) == 2

        # Test health score calculation
        healthy_parcel = LandParcel.query.filter_by(name='Test Farm A').first()
        assert healthy_parcel.health_score == 76  # (8*0.6 + 7*0.4)*10
        assert healthy_parcel.risk_level == 'Low'
        assert healthy_parcel.risk_color == 'green'

        # Test risk parcel
        risk_parcel = LandParcel.query.filter_by(name='Test Farm B').first()
        assert risk_parcel.health_score == 36  # (4*0.6 + 3*0.4)*10
        assert risk_parcel.risk_level == 'Medium'
        assert risk_parcel.risk_color == 'yellow'

    def test_parcel_relationships(self, init_database):
        """Test user-parcel relationships."""
        user = User.query.first()
        assert len(user.parcels) == 2
        assert user.parcels[0].name == 'Test Farm A'

    def test_health_score_edge_cases(self):
        """Test health scoring with edge cases."""
        # Test minimum scores
        min_parcel = LandParcel(soil_quality=1, vegetation_cover=1)
        min_parcel.health_score = LandParcel.calculate_health_score(1, 1)
        min_parcel.risk_level, min_parcel.risk_label, min_parcel.risk_color = LandParcel.get_risk_category(min_parcel.health_score)
        assert min_parcel.health_score == 10

        # Test maximum scores
        max_parcel = LandParcel(soil_quality=10, vegetation_cover=10)
        max_parcel.health_score = LandParcel.calculate_health_score(10, 10)
        max_parcel.risk_level, max_parcel.risk_label, max_parcel.risk_color = LandParcel.get_risk_category(max_parcel.health_score)
        assert max_parcel.health_score == 100

        # Test medium risk
        medium_parcel = LandParcel(soil_quality=6, vegetation_cover=5)
        medium_parcel.health_score = LandParcel.calculate_health_score(6, 5)
        medium_parcel.risk_level, medium_parcel.risk_label, medium_parcel.risk_color = LandParcel.get_risk_category(medium_parcel.health_score)
        assert medium_parcel.health_score == 56
        assert medium_parcel.risk_level == 'Medium'