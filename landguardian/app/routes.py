from flask import Blueprint, render_template, request, redirect, url_for, jsonify, abort

from app import db
from app.models import LandParcel

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    """
    Dashboard route displaying land parcel statistics and list.
    """
    parcels = LandParcel.query.all()
    total_parcels = len(parcels)
    high_risk_count = sum(1 for p in parcels if p.risk_level == 'High')
    average_health = sum(p.health_score for p in parcels) / total_parcels if total_parcels > 0 else 0
    stats = {
        'total': total_parcels,
        'high_risk': high_risk_count,
        'average_health': round(average_health, 1)
    }
    parcels_data = [
        {
            'id': p.id,
            'name': p.name,
            'location': p.location,
            'latitude': p.latitude,
            'longitude': p.longitude,
            'risk_level': p.risk_level
        } for p in parcels
    ]
    return render_template('dashboard.html', parcels=parcels, stats=stats, parcels_data=parcels_data)

@main_bp.route('/add', methods=['GET', 'POST'])
def add_parcel():
    """
    Route for adding new land parcels.
    GET: Display form
    POST: Process form and create new parcel
    """
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        latitude = float(request.form.get('latitude') or 0)
        longitude = float(request.form.get('longitude') or 0)
        soil_quality = int(request.form['soil_quality'])
        vegetation_cover = int(request.form['vegetation_cover'])
        health_score = LandParcel.calculate_health_score(soil_quality, vegetation_cover)
        risk_level, risk_label, risk_color = LandParcel.get_risk_category(health_score)
        parcel = LandParcel(
            name=name,
            location=location,
            latitude=latitude,
            longitude=longitude,
            soil_quality=soil_quality,
            vegetation_cover=vegetation_cover,
            health_score=health_score,
            risk_level=risk_level,
            risk_label=risk_label,
            risk_color=risk_color
        )
        db.session.add(parcel)
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    return render_template('add_parcel.html')

@main_bp.route('/parcel/<int:parcel_id>')
def parcel_detail(parcel_id):
    """
    Route for displaying individual parcel details.
    """
    parcel = LandParcel.query.get_or_404(parcel_id)
    return render_template('parcel_detail.html', parcel=parcel)

@main_bp.route('/api/health-trend/<int:parcel_id>')
def health_trend(parcel_id):
    """
    API endpoint for parcel health trend data.
    """
    parcel = LandParcel.query.get_or_404(parcel_id)
    # Dummy trend data for demonstration
    trend = [
        {'date': '2023-01', 'score': max(0, parcel.health_score - 5)},
        {'date': '2023-02', 'score': max(0, parcel.health_score - 2)},
        {'date': '2023-03', 'score': parcel.health_score},
    ]
    return jsonify(trend)