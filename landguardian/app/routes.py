from flask import Blueprint, render_template, request, redirect, url_for, jsonify, abort, flash, session, Response, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from datetime import datetime
import re
import logging
import csv
from io import StringIO
import tempfile

from app import db, mail
from app.models import LandParcel, User
from app.recommendations import get_recommendations, generate_soil_recommendations, generate_vegetation_recommendations
from app.utils.predictor import TrendPredictor
from utils.pdf_export import generate_parcels_pdf

main_bp = Blueprint('main', __name__)

def get_tour_dummy_data():
    """
    Generate dummy data for tour demonstration with AI features.
    Returns dummy parcels and statistics for users taking the tour.
    """
    predictor = TrendPredictor()

    dummy_parcels = [
        {
            'id': 'demo-1',
            'name': 'North Farm Field A',
            'location': 'North Farm',
            'latitude': 37.7749,
            'longitude': -122.4194,
            'soil_quality': 8,
            'vegetation_cover': 7,
            'health_score': LandParcel.calculate_health_score(8, 7),
            'risk_level': 'Low',
            'risk_label': 'Low Risk',
            'risk_color': 'green',
            'last_updated': datetime.utcnow(),
            # Add AI prediction data
            'ai_prediction': predictor.predict_future_health(predictor.generate_historical_data(LandParcel.calculate_health_score(8, 7))),
            'historical_data': predictor.generate_historical_data(LandParcel.calculate_health_score(8, 7))
        },
        {
            'id': 'demo-2',
            'name': 'South Valley Plot',
            'location': 'South Valley',
            'latitude': 37.7510,
            'longitude': -122.4180,
            'soil_quality': 4,
            'vegetation_cover': 3,
            'health_score': LandParcel.calculate_health_score(4, 3),
            'risk_level': 'High',
            'risk_label': 'High Risk',
            'risk_color': 'red',
            'last_updated': datetime.utcnow(),
            # Add AI prediction data
            'ai_prediction': predictor.predict_future_health(predictor.generate_historical_data(LandParcel.calculate_health_score(4, 3))),
            'historical_data': predictor.generate_historical_data(LandParcel.calculate_health_score(4, 3))
        },
        {
            'id': 'demo-3',
            'name': 'East Hills Section',
            'location': 'East Hills',
            'latitude': 37.7850,
            'longitude': -122.4100,
            'soil_quality': 6,
            'vegetation_cover': 5,
            'health_score': LandParcel.calculate_health_score(6, 5),
            'risk_level': 'Medium',
            'risk_label': 'Medium Risk',
            'risk_color': 'yellow',
            'last_updated': datetime.utcnow(),
            # Add AI prediction data
            'ai_prediction': predictor.predict_future_health(predictor.generate_historical_data(LandParcel.calculate_health_score(6, 5))),
            'historical_data': predictor.generate_historical_data(LandParcel.calculate_health_score(6, 5))
        }
    ]

    # Calculate statistics from dummy data
    total_parcels = len(dummy_parcels)
    high_risk_count = sum(1 for p in dummy_parcels if p['risk_level'] == 'High')
    medium_risk_count = sum(1 for p in dummy_parcels if p['risk_level'] == 'Medium')
    average_health = sum(p['health_score'] for p in dummy_parcels) / total_parcels

    # Calculate AI insights for dummy data
    declining_parcels = sum(1 for p in dummy_parcels if p['ai_prediction'][2] == "declining")

    stats = {
        'total': total_parcels,
        'high_risk': high_risk_count,
        'medium_risk': medium_risk_count,
        'average_health': round(average_health, 1),
        'declining_parcels': declining_parcels
    }

    return dummy_parcels, stats

@main_bp.route('/')
@login_required
def dashboard():
    """
    Dashboard route displaying land parcel statistics and list.
    For tour users, shows dummy data to demonstrate full interface.
    """
    parcels = LandParcel.query.filter_by(user_id=current_user.id).all()
    came_from_tour = request.args.get('tour') == 'true'

    # Calculate AI insights
    predictor = TrendPredictor()
    declining_parcels = 0
    for parcel in parcels:
        historical = predictor.generate_historical_data(parcel.health_score)
        _, _, trend = predictor.predict_future_health(historical)
        if trend == "declining":
            declining_parcels += 1

    # Initialize stats
    stats = {}

    # Use dummy data for tour visitors with no parcels
    if came_from_tour and len(parcels) == 0:
        parcels, stats = get_tour_dummy_data()
        parcels_data = parcels  # Use dummy parcels for map
        is_first_visit = False  # Show full dashboard for tour
        declining_parcels = stats['declining_parcels']  # Use pre-calculated AI insights
    else:
        # Normal logic for regular users
        total_parcels = len(parcels)
        high_risk_count = sum(1 for p in parcels if p.risk_level == 'High')
        medium_risk_count = sum(1 for p in parcels if p.risk_level == 'Medium')
        average_health = sum(p.health_score for p in parcels) / total_parcels if total_parcels > 0 else 0
        stats = {
            'total': total_parcels,
            'high_risk': high_risk_count,
            'medium_risk': medium_risk_count,
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

        # Calculate AI insights for regular users
        declining_parcels = 0
        for parcel in parcels:
            historical = predictor.generate_historical_data(parcel.health_score)
            _, _, trend = predictor.predict_future_health(historical)
            if trend == "declining":
                declining_parcels += 1

    map_style = current_user.preferences.get('map_style', 'satellite')
    show_tour = came_from_tour  # Only show tour for tour visitors

    # Generate recommendation summaries for high-priority parcels
    high_risk_parcels = [p for p in parcels if isinstance(p, dict) and p.get('risk_level') == "High" or hasattr(p, 'risk_level') and p.risk_level == "High"]
    medium_risk_parcels = [p for p in parcels if isinstance(p, dict) and p.get('risk_level') == "Medium" or hasattr(p, 'risk_level') and p.risk_level == "Medium"]

    # Get top recommendations for high-risk parcels
    urgent_recommendations = []
    for parcel in high_risk_parcels[:3]:  # Limit to top 3 high-risk parcels
        soil_quality = parcel.soil_quality if hasattr(parcel, 'soil_quality') else parcel.get('soil_quality', 5)
        vegetation_cover = parcel.vegetation_cover if hasattr(parcel, 'vegetation_cover') else parcel.get('vegetation_cover', 5)
        health_score = parcel.health_score if hasattr(parcel, 'health_score') else parcel.get('health_score', 50)
        name = parcel.name if hasattr(parcel, 'name') else parcel.get('name', 'Unknown Parcel')

        soil_recs = generate_soil_recommendations(soil_quality)
        veg_recs = generate_vegetation_recommendations(vegetation_cover)
        urgent_recommendations.append({
            'parcel_name': name,
            'priority_action': f"⚠️ IMMEDIATE: Health score {health_score}% - Critical attention needed",
            'top_soil_rec': soil_recs[0] if soil_recs else None,
            'top_veg_rec': veg_recs[0] if veg_recs else None
        })

    return render_template('dashboard.html', parcels=parcels, stats=stats, parcels_data=parcels_data, is_first_visit=is_first_visit, map_style=map_style, show_tour=show_tour, came_from_tour=came_from_tour, urgent_recommendations=urgent_recommendations, declining_parcels=declining_parcels)

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

    # Get AI prediction for recommendations
    predictor = TrendPredictor()
    historical_scores = predictor.generate_historical_data(parcel.health_score)
    predicted_score, confidence, trend = predictor.predict_future_health(historical_scores)

    # Pass AI insights to recommendations
    recommendations = get_recommendations(parcel, trend, confidence)

    return render_template('parcel_detail.html', parcel=parcel, recommendations=recommendations)

@main_bp.route('/api/health-trend/<parcel_id>')
@login_required
def health_trend(parcel_id):
    """
    API endpoint for parcel health trend data with AI predictions.
    Supports both real parcel IDs and demo IDs for tour mode.
    """
    # Handle demo parcels for tour mode
    if parcel_id.startswith('demo-'):
        # Get dummy data for tour demonstration
        dummy_parcels, _ = get_tour_dummy_data()
        parcel_data = next((p for p in dummy_parcels if p['id'] == parcel_id), None)
        if not parcel_data:
            abort(404)

        # Use pre-calculated AI data from dummy parcel
        historical_scores = parcel_data['historical_data']
        predicted_score, confidence, trend = parcel_data['ai_prediction']
    else:
        # Handle real parcels
        parcel = LandParcel.query.get_or_404(int(parcel_id))
        if parcel.user_id != current_user.id:
            abort(404)

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
            user.total_logins += 1
            db.session.commit()
            session.pop('login_attempts', None)

            # Redirect to welcome page if user has no parcels
            if LandParcel.query.filter_by(user_id=user.id).count() == 0:
                return redirect(url_for('main.welcome'))

            return redirect(url_for('main.dashboard'))

        session['login_attempts'] = attempts + 1
        flash('Invalid email or password', 'error')

    return render_template('login.html')

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


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

@main_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """
    User settings page for preferences.
    """
    if request.method == 'POST':
        current_user.preferences['units'] = request.form['units']
        current_user.preferences['map_style'] = request.form['map_style']
        current_user.preferences['notifications']['email'] = 'email' in request.form
        current_user.preferences['notifications']['browser'] = 'browser' in request.form
        db.session.commit()
        flash('Settings updated successfully', 'success')
        return redirect(url_for('main.settings'))

    return render_template('settings.html')

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    User profile page with edit functionality.
    """
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            current_user.name = request.form['name']
            current_user.organization = request.form.get('organization')
            db.session.commit()
            flash('Profile updated successfully', 'success')

        elif action == 'change_password':
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']

            if not current_user.check_password(current_password):
                flash('Current password is incorrect', 'error')
            elif len(new_password) < 8:
                flash('New password must be at least 8 characters long', 'error')
            elif not re.match(r'^(?=.*[A-Za-z])(?=.*\d)', new_password):
                flash('New password must contain at least one letter and one number', 'error')
            elif new_password != confirm_password:
                flash('New passwords do not match', 'error')
            else:
                current_user.set_password(new_password)
                db.session.commit()
                flash('Password changed successfully', 'success')

        elif action == 'delete_account':
            if request.form.get('confirm_delete') == 'DELETE':
                # Delete all user's parcels first
                LandParcel.query.filter_by(user_id=current_user.id).delete()
                db.session.delete(current_user)
                db.session.commit()
                logout_user()
                flash('Account deleted successfully', 'info')
                return redirect(url_for('main.login'))
            else:
                flash('Please type "DELETE" to confirm account deletion', 'error')

        return redirect(url_for('main.profile'))

    # Calculate profile completion
    total_parcels = LandParcel.query.filter_by(user_id=current_user.id).count()
    completion = 0
    if current_user.name: completion += 25
    if current_user.organization: completion += 25
    if current_user.total_logins > 0: completion += 25
    if total_parcels > 0: completion += 25

    # Recent activity (simplified)
    recent_activity = []
    parcels = LandParcel.query.filter_by(user_id=current_user.id).order_by(LandParcel.last_updated.desc()).limit(5).all()
    for parcel in parcels:
        recent_activity.append(f"Updated parcel '{parcel.name}'")

    return render_template('profile.html',
                         completion=completion,
                         recent_activity=recent_activity,
                         total_parcels=total_parcels)

@main_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Handle password reset requests with rate limiting.
    """
    # Rate limiting: 3 attempts per hour per IP
    attempts_key = f"forgot_password_{request.remote_addr}"
    attempts = session.get(attempts_key, [])
    attempts = [t for t in attempts if datetime.utcnow().timestamp() - t < 3600]  # Remove old attempts

    if len(attempts) >= 3:
        flash('Too many reset attempts. Please try again later.', 'error')
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()

        if user:
            token = user.generate_reset_token()
            reset_url = url_for('main.reset_password', token=token, _external=True)

            msg = Message('Password Reset Request - LandGuardian',
                          sender=current_app.config['MAIL_DEFAULT_SENDER'],
                          recipients=[email])
            msg.body = f'''Hello {user.name},

You have requested to reset your password for your LandGuardian account.

To reset your password, please click the following link:
{reset_url}

This link will expire in 1 hour for security reasons.

If you did not request this password reset, please ignore this email. Your password will remain unchanged.

For security reasons, please do not share this email with anyone.

Best regards,
The LandGuardian Team
'''
            try:
                mail.send(msg)
                flash('Password reset link has been sent to your email.', 'info')
                logging.info(f'Password reset email sent to {email}')
            except Exception as e:
                flash('Error sending email. Please try again later.', 'error')
                logging.error(f'Failed to send password reset email to {email}: {str(e)}')
        else:
            flash('If an account with that email exists, a password reset link has been sent.', 'info')

        # Record attempt
        attempts.append(datetime.utcnow().timestamp())
        session[attempts_key] = attempts

        return redirect(url_for('main.login'))

    return render_template('forgot_password.html')

@main_bp.route('/welcome')
@login_required
def welcome():
    """
    Welcome page for new users with no parcels.
    """
    return render_template('welcome.html')

@main_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Handle password reset with token validation.
    """
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid or expired reset token', 'error')
        logging.warning(f'Invalid password reset attempt with token: {token[:10]}...')
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Password strength validation
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return redirect(url_for('main.reset_password', token=token))

        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)', password):
            flash('Password must contain at least one letter and one number', 'error')
            return redirect(url_for('main.reset_password', token=token))

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('main.reset_password', token=token))

        user.set_password(password)
        db.session.commit()

        # Auto login
        login_user(user)

        flash('Password has been reset successfully. You are now logged in.', 'success')
        logging.info(f'Password reset successful for user: {user.email}')

        return redirect(url_for('main.dashboard'))

    return render_template('reset_password.html')

@main_bp.route('/export/csv')
@login_required
def export_csv():
    """
    Export user's land parcels data as CSV file.
    Supports both bulk export (all parcels) and single parcel export.
    """
    parcel_id = request.args.get('parcel_id', type=int)

    if parcel_id:
        parcel = LandParcel.query.get_or_404(parcel_id)
        if parcel.user_id != current_user.id:
            abort(404)
        parcels = [parcel]
        filename = f"parcel_{parcel_id}_export.csv"
    else:
        parcels = LandParcel.query.filter_by(user_id=current_user.id).all()
        filename = "landguardian_export.csv"

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Location', 'Soil Quality', 'Vegetation Cover',
                    'Health Score', 'Risk Level', 'Last Updated'])

    for parcel in parcels:
        writer.writerow([
            parcel.name,
            parcel.location,
            parcel.soil_quality,
            parcel.vegetation_cover,
            parcel.health_score,
            parcel.risk_label,
            parcel.last_updated.strftime('%Y-%m-%d')
        ])

    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

@main_bp.route('/export/pdf')
@login_required
def export_pdf():
    """
    Export user's land parcels data as PDF report.
    """
    # Get parcels for current user only
    parcels = LandParcel.query.filter_by(user_id=current_user.id).all()

    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        generate_parcels_pdf(parcels, tmp.name)
        tmp.seek(0)
        pdf_data = tmp.read()

    return Response(
        pdf_data,
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment;filename=landguardian_report.pdf"}
    )