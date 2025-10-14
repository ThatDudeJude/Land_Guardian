import pytest
import numpy as np
from app.utils.predictor import TrendPredictor
from app.recommendations import get_recommendations, generate_soil_recommendations
from app.models import LandParcel

class TestUtilities:
    def test_trend_predictor(self):
        """Test AI trend prediction functionality."""
        predictor = TrendPredictor()

        # Test with improving trend
        improving_scores = [50, 55, 60, 65, 70, 75]
        prediction, confidence, trend = predictor.predict_future_health(improving_scores)
        assert 0 <= prediction <= 100
        assert 0 <= confidence <= 1
        assert trend in ['improving', 'declining', 'stable']

        # Test with declining trend
        declining_scores = [75, 70, 65, 60, 55, 50]
        prediction, confidence, trend = predictor.predict_future_health(declining_scores)
        assert trend == 'declining'

    def test_insufficient_data_prediction(self):
        """Test prediction with insufficient data."""
        predictor = TrendPredictor()
        prediction, confidence, trend = predictor.predict_future_health([50, 55])
        assert trend == 'stable'  # Should fall back to stable

    def test_soil_recommendations(self):
        """Test soil recommendation generation."""
        # Test critical soil
        critical_recs = generate_soil_recommendations(2)
        assert len(critical_recs) > 0
        assert 'CRITICAL' in critical_recs[0]

        # Test good soil
        good_recs = generate_soil_recommendations(9)
        assert 'excellent' in good_recs[0].lower()

    def test_complete_recommendations(self, init_database):
        """Test complete recommendation system."""
        parcel = LandParcel.query.first()
        recommendations = get_recommendations(parcel)

        assert 'soil' in recommendations
        assert 'vegetation' in recommendations
        assert 'priority' in recommendations
        assert len(recommendations['soil']) > 0
        assert len(recommendations['vegetation']) > 0

    def test_historical_data_generation(self):
        """Test mock historical data generation."""
        predictor = TrendPredictor()
        historical_data = predictor.generate_historical_data(70)

        assert len(historical_data) == 6
        assert all(10 <= score <= 100 for score in historical_data)
        # Should show an upward trend ending at approximately 70
        assert historical_data[-1] >= historical_data[0]