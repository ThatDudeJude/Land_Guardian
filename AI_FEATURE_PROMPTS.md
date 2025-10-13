# **STEP-BY-STEP AI IMPLEMENTATION PROMPTS**

Here are the steps you will take to implement AI prediction of land health. You can adapt the example code to the existing codebase if there is any conflict in implementation. Use this as a guide, not canon.

## **STEP 1: DEPENDENCIES & PREDICTOR CLASS**


Add machine learning dependencies and create the trend predictor class for LandGuardian.

1. Update requirements.txt to include:
```
scikit-learn==1.3.0
numpy==1.24.3
```

2. Create app/utils/predictor.py with this code:

```python
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
```

3. Test the predictor works by running:

```python
p = TrendPredictor()
test_scores = [60, 62, 65, 63, 68, 70]
print(p.predict_future_health(test_scores))
```

Make sure the file structure is: app/utils/predictor.py


## **STEP 2: UPDATE HEALTH TREND API**



Update the health trend API to use the machine learning predictor.


1. In app/routes.py, add the import:
```python
from app.utils.predictor import TrendPredictor
```

2. Replace the existing health_trend API endpoint with:
```python
@app.route('/api/health-trend/<int:parcel_id>')
def health_trend(parcel_id):
    parcel = LandParcel.query.get_or_404(parcel_id)
    
    # Generate historical data using the predictor
    predictor = TrendPredictor()
    historical_scores = predictor.generate_historical_data(parcel.health_score)
    
    # Get AI prediction
    predicted_score, confidence, trend = predictor.predict_future_health(historical_scores)
    
    # Create dates for historical data
    dates = [f"Month {i+1}" for i in range(len(historical_scores))]
    
    return jsonify({
        'historical': {
            'dates': dates,
            'scores': historical_scores
        },
        'prediction': {
            'next_score': round(predicted_score, 1),
            'confidence': round(confidence, 2),
            'trend': trend,
            'date': 'Next Month'
        },
        'ai_generated': True
    })
```

3. Test the API endpoint by:
- Running the Flask app
- Visiting: http://localhost:5000/api/health-trend/1
- You should see JSON with historical data and AI prediction

Make sure the response includes 'ai_generated': true and prediction data.


## **STEP 3: ADD AI PREDICTION CARD TO PARCEL DETAIL**

Add an AI prediction card to the parcel detail page.

1. In templates/parcel_detail.html, add this card after the recommendations section:
```html
<!-- AI Prediction Card -->
<div class="card mt-4">
    <div class="card-header bg-primary text-white">
        <h5 class="card-title mb-0">🤖 AI Health Prediction</h5>
    </div>
    <div class="card-body">
        <div id="predictionContainer">
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading AI prediction...</span>
                </div>
                <p class="mt-2">Analyzing trends with machine learning...</p>
            </div>
        </div>
    </div>
</div>
```

2. Add this JavaScript to fetch and display predictions:

```html
<script>
document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/health-trend/{{ parcel.id }}')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('predictionContainer');
            
            if (data.ai_generated) {
                const prediction = data.prediction;
                const trendIcon = prediction.trend === 'improving' ? '📈' : 
                                prediction.trend === 'declining' ? '📉' : '➡️';
                const trendColor = prediction.trend === 'improving' ? 'success' : 
                                 prediction.trend === 'declining' ? 'danger' : 'secondary';
                
                container.innerHTML = `
                    <div class="row text-center">
                        <div class="col-md-4">
                            <h3 class="text-${trendColor}">${prediction.next_score}%</h3>
                            <small class="text-muted">Predicted Score</small>
                        </div>
                        <div class="col-md-4">
                            <h3>${trendIcon}</h3>
                            <small class="text-${trendColor}">${prediction.trend}</small>
                        </div>
                        <div class="col-md-4">
                            <h3>${Math.round(prediction.confidence * 100)}%</h3>
                            <small class="text-muted">AI Confidence</small>
                        </div>
                    </div>
                    <div class="progress mt-3" style="height: 10px;">
                        <div class="progress-bar bg-${trendColor}" 
                             style="width: ${Math.round(prediction.confidence * 100)}%">
                        </div>
                    </div>
                    <div class="mt-2">
                        <small class="text-muted">
                            <i>Machine learning prediction based on historical trend analysis</i>
                        </small>
                    </div>
                `;
            } else {
                container.innerHTML = `
                    <p class="text-muted text-center">
                        <i>Collect more data to enable AI predictions</i>
                    </p>
                `;
            }
        })
        .catch(error => {
            container.innerHTML = `
                <p class="text-danger text-center">
                    <i>Unable to load AI prediction</i>
                </p>
            `;
        });
});
</script>
```


## **STEP 4: ENHANCE RECOMMENDATIONS WITH AI INSIGHTS**


Enhance the recommendation system with AI-powered insights.

1. In app/utils/recommendations.py, add this function:
```python
def get_ai_enhanced_insight(predicted_trend, confidence):
    """Add AI-powered insights based on predictions"""
    if confidence < 0.6:
        return "More data needed for reliable AI predictions"
    
    if predicted_trend == "declining":
        return "🤖 AI predicts potential decline - consider preventive measures"
    elif predicted_trend == "improving":
        return "🤖 AI predicts improvement - current practices are effective"
    else:
        return "🤖 AI predicts stable conditions - maintain current management"
```

2. Update the get_recommendations function to include AI insights:
```python
def get_recommendations(parcel, predicted_trend=None, confidence=0):
    soil_recs = generate_soil_recommendations(parcel.soil_quality)
    veg_recs = generate_vegetation_recommendations(parcel.vegetation_cover)
    priority = get_priority_action(parcel.risk_level, parcel.health_score)
    
    # Add AI insight if available
    ai_insight = ""
    if predicted_trend:
        ai_insight = get_ai_enhanced_insight(predicted_trend, confidence)
        priority = f"{priority} {ai_insight}"
    
    return {
        'soil': soil_recs,
        'vegetation': veg_recs,
        'priority': priority,
        'uses_ai': bool(predicted_trend)
    }
```

3. Update the parcel_detail route in app/routes.py to pass AI insights:
```python
@app.route('/parcel/<int:parcel_id>')
def parcel_detail(parcel_id):
    parcel = LandParcel.query.get_or_404(parcel_id)
    
    # Get AI prediction for recommendations
    predictor = TrendPredictor()
    historical_scores = predictor.generate_historical_data(parcel.health_score)
    predicted_score, confidence, trend = predictor.predict_future_health(historical_scores)
    
    # Pass AI insights to recommendations
    recommendations = get_recommendations(parcel, trend, confidence)
    
    return render_template('parcel_detail.html', 
                         parcel=parcel, 
                         recommendations=recommendations)
```

4. Test by checking if recommendations now include AI insights on parcel detail pages.

## **STEP 5: DASHBOARD AI SUMMARY**

**Prompt for Grok:**
```
Add an AI insights summary to the dashboard.

1. In app/routes.py, update the dashboard route to calculate AI insights:
```python
@app.route('/')
def dashboard():
    parcels = LandParcel.query.all()
    total_parcels = len(parcels)
    high_risk_count = len([p for p in parcels if p.risk_level == "high"])
    avg_health = sum(p.health_score for p in parcels) / total_parcels if total_parcels else 0
    
    # Calculate AI insights
    predictor = TrendPredictor()
    declining_parcels = 0
    for parcel in parcels:
        historical = predictor.generate_historical_data(parcel.health_score)
        _, _, trend = predictor.predict_future_health(historical)
        if trend == "declining":
            declining_parcels += 1
    
    return render_template('dashboard.html', 
                         parcels=parcels,
                         total_parcels=total_parcels,
                         high_risk_count=high_risk_count,
                         avg_health=avg_health,
                         declining_parcels=declining_parcels)
```

2. In templates/dashboard.html, add an AI insights card to the statistics section:
```html
<!-- Add this card to the statistics row -->
<div class="col-md-3">
    <div class="card text-white bg-info">
        <div class="card-body">
            <h5 class="card-title">🤖 AI Insights</h5>
            <h2 class="card-text">{{ declining_parcels }}</h2>
            <p class="card-text">Parcels predicted to decline</p>
        </div>
    </div>
</div>
```

3. Update the statistics row to have 4 columns instead of 3 (adjust existing col-md-4 to col-md-3).



