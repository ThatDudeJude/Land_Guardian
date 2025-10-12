from flask import Blueprint, render_template, request, redirect, url_for, jsonify, abort, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
import re

from app import db
from app.models import LandParcel, User

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def dashboard():
    """
    Dashboard route displaying land parcel statistics and list.
    """
    parcels = LandParcel.query.filter_by(user_id=current_user.id).all()
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
            'risk_level': p.risk_level,
            'health_score': p.health_score,
            'risk_label': p.risk_label,
            'soil_quality': p.soil_quality,
            'vegetation_cover': p.vegetation_cover,
            'risk_color': p.risk_color
        } for p in parcels
    ]
    is_first_visit = len(parcels) == 0
    return render_template('dashboard.html', parcels=parcels, stats=stats, parcels_data=parcels_data, is_first_visit=is_first_visit)

@main_bp.route('/add', methods=['GET', 'POST'])
@login_required
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
            risk_color=risk_color,
            user_id=current_user.id
        )
        db.session.add(parcel)
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    return render_template('add_parcel.html')

@main_bp.route('/parcel/<int:parcel_id>')
@login_required
def parcel_detail(parcel_id):
    """
    Route for displaying individual parcel details.
    """
    parcel = LandParcel.query.get_or_404(parcel_id)
    if parcel.user_id != current_user.id:
        abort(404)
    return render_template('parcel_detail.html', parcel=parcel)

@main_bp.route('/api/health-trend/<int:parcel_id>')
@login_required
def health_trend(parcel_id):
    """
    API endpoint for parcel health trend data.
    """
    parcel = LandParcel.query.get_or_404(parcel_id)
    if parcel.user_id != current_user.id:
        abort(404)
    # Dummy trend data for demonstration
    trend = [
        {'date': '2023-01', 'score': max(0, parcel.health_score - 5)},
        {'date': '2023-02', 'score': max(0, parcel.health_score - 2)},
        {'date': '2023-03', 'score': parcel.health_score},
    ]
    return jsonify(trend)

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        name = request.form['name']
        organization = request.form.get('organization')
        role = request.form['role']

        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return redirect(url_for('main.register'))

        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)', password):
            flash('Password must contain at least one letter and one number', 'error')
            return redirect(url_for('main.register'))

        common_passwords = ['password', '123456', 'qwerty', 'password123']
        if password.lower() in common_passwords:
            flash('Please choose a stronger password', 'error')
            return redirect(url_for('main.register'))

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('main.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('main.register'))

        user = User(email=email, name=name, organization=organization, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful', 'success')
        return redirect(url_for('main.welcome'))

    return render_template('register.html')

@main_bp.route('/welcome')
@login_required
def welcome():
    """
    Welcome page for new users with onboarding guidance.
    """
    return render_template('welcome.html')

@main_bp.route('/load-sample-data', methods=['POST'])
@login_required
def load_sample_data():
    """
    Load sample parcels for new users.
    """
    if LandParcel.query.filter_by(user_id=current_user.id).count() > 0:
        return jsonify({'success': False, 'message': 'Sample data already loaded'})

    samples = [
        {
            'name': 'Sample Farm A',
            'location': 'Northern Valley',
            'latitude': 37.7749,
            'longitude': -122.4194,
            'soil_quality': 8,
            'vegetation_cover': 7
        },
        {
            'name': 'Sample Farm B',
            'location': 'Southern Hills',
            'latitude': 37.7849,
            'longitude': -122.4094,
            'soil_quality': 5,
            'vegetation_cover': 4
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
            risk_color=risk_color,
            user_id=current_user.id
        )
        db.session.add(parcel)
    db.session.commit()
    return jsonify({'success': True})

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        attempts = session.get('login_attempts', 0)
        if attempts >= 5:
            flash('Too many login attempts. Please try again later.', 'error')
            return redirect(url_for('main.login'))

        email = request.form['email']
        password = request.form['password']
        remember = 'remember' in request.form

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            session.pop('login_attempts', None)
            return redirect(url_for('main.dashboard'))

        session['login_attempts'] = attempts + 1
        flash('Invalid email or password', 'error')

    return render_template('login.html')

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form['name']
        current_user.organization = request.form.get('organization')
        current_user.role = request.form['role']
        db.session.commit()
        flash('Profile updated', 'success')
        return redirect(url_for('main.profile'))

    return render_template('profile.html')

@main_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if not current_user.check_password(old_password):
            flash('Old password is incorrect', 'error')
            return redirect(url_for('main.change_password'))

        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return redirect(url_for('main.change_password'))

        current_user.set_password(new_password)
        db.session.commit()
        flash('Password changed successfully', 'success')
        return redirect(url_for('main.profile'))

    return render_template('change_password.html')