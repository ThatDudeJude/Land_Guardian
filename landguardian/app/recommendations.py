"""
Recommendation engine for LandGuardian land degradation monitoring system.
Provides actionable recommendations based on soil quality, vegetation cover, and risk levels.
"""

def generate_soil_recommendations(soil_score):
    """
    Generate soil management recommendations based on soil quality score.

    Args:
        soil_score (int): Soil quality score (1-10)

    Returns:
        list: List of recommendation strings with appropriate urgency indicators
    """
    if soil_score <= 3:
        return [
            "🌱 CRITICAL: Add organic compost immediately",
            "💧 Test soil nutrients and pH levels",
            "🔄 Implement cover cropping with legumes",
            "🚫 Avoid chemical fertilizers until soil recovers"
        ]
    elif soil_score <= 6:
        return [
            "🌱 Add compost or organic matter",
            "📊 Consider soil testing for specific deficiencies",
            "🔄 Practice crop rotation",
            "💧 Monitor soil moisture regularly"
        ]
    else:
        return [
            "✅ Soil quality is excellent",
            "📝 Document your successful practices",
            "🌿 Continue current soil management",
            "📈 Monitor for any changes"
        ]

def generate_vegetation_recommendations(vegetation_score):
    """
    Generate vegetation management recommendations based on vegetation cover score.

    Args:
        vegetation_score (int): Vegetation cover score (1-10)

    Returns:
        list: List of recommendation strings with appropriate urgency indicators
    """
    if vegetation_score <= 3:
        return [
            "🌳 CRITICAL: Plant native tree species",
            "🚫 Implement controlled grazing or reduce livestock",
            "💧 Consider irrigation if rainfall is insufficient",
            "🌾 Introduce perennial ground cover"
        ]
    elif vegetation_score <= 6:
        return [
            "📈 Monitor vegetation growth patterns",
            "🌾 Consider diversifying plant species",
            "💧 Ensure adequate water supply",
            "📊 Assess grazing pressure"
        ]
    else:
        return [
            "✅ Vegetation cover is excellent",
            "🦋 Support biodiversity with native plants",
            "📝 Document successful vegetation management",
            "🌿 Continue current practices"
        ]

def get_priority_action(risk_level, health_score):
    """
    Generate priority action based on overall risk level and health score.

    Args:
        risk_level (str): Risk level ('low', 'medium', 'high')
        health_score (int): Overall health score (0-100)

    Returns:
        str: Priority action message with urgency indicators
    """
    if risk_level == "high":
        return f"⚠️ IMMEDIATE ACTION REQUIRED: Health score {health_score}% - Implement erosion control and soil conservation"
    elif risk_level == "medium":
        return f"⚠️ MONITOR CLOSELY: Health score {health_score}% - Consider preventive measures"
    else:
        return f"✅ STABLE: Health score {health_score}% - Continue current management"

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

def get_recommendations(parcel, predicted_trend=None, confidence=0):
    """
    Generate comprehensive recommendations for a land parcel.

    Args:
        parcel: LandParcel model instance with soil_quality, vegetation_cover,
                risk_level, and health_score attributes
        predicted_trend (str, optional): AI predicted trend ('improving', 'declining', 'stable')
        confidence (float, optional): AI prediction confidence (0-1)

    Returns:
        dict: Dictionary containing soil, vegetation, priority recommendations, and AI flag
    """
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