import numpy as np
from sklearn.linear_model import LinearRegression
import random

class TrendPredictor:
    def __init__(self):
        self.linear_model = LinearRegression()

    def predict_future_health(self, historical_scores):
        """
        Predict future health scores using linear regression
        Returns: predicted_score, confidence, trend_direction
        """
        if len(historical_scores) < 3:
            # Not enough data for ML, use simple average
            avg_score = np.mean(historical_scores) if historical_scores else 50
            return avg_score, 0.5, "stable"

        try:
            # Prepare data for linear regression
            X = np.array(range(len(historical_scores))).reshape(-1, 1)
            y = np.array(historical_scores)

            # Train model
            self.linear_model.fit(X, y)

            # Predict next period
            next_x = np.array([[len(historical_scores)]])
            prediction = self.linear_model.predict(next_x)[0]

            # Calculate confidence (R² score)
            confidence = max(0.3, min(0.9, self.linear_model.score(X, y)))

            # Determine trend
            current_score = historical_scores[-1]
            if prediction > current_score + 2:
                trend = "improving"
            elif prediction < current_score - 2:
                trend = "declining"
            else:
                trend = "stable"

            return max(0, min(100, prediction)), confidence, trend

        except Exception:
            # Fallback to simple average
            avg_score = np.mean(historical_scores)
            return avg_score, 0.3, "stable"

    def generate_historical_data(self, current_score, periods=6):
        """Generate realistic historical data for demo purposes"""
        historical = []
        base_score = max(20, current_score - random.randint(5, 15))

        for i in range(periods):
            # Create a realistic trend with some noise
            trend = (current_score - base_score) / periods
            score = base_score + (trend * i) + random.randint(-5, 5)
            historical.append(max(10, min(100, score)))

        return historical