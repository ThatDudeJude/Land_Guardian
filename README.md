# LandGuardian 🌱

**Land Degradation Monitoring System** - A comprehensive Flask web application for monitoring land health, tracking degradation trends, and providing actionable recommendations for sustainable land management.

## 🎯 Overview

LandGuardian addresses SDG 15 (Life on Land) by providing farmers, researchers, and policymakers with tools to monitor land degradation, predict future trends using AI, and implement preventive measures. The system combines traditional soil/vegetation monitoring with machine learning predictions to help combat desertification and land degradation.

## ✨ Key Features 

### 🏠 Dashboard & Visualization
- **Interactive Map**: Leaflet-powered map with color-coded risk markers
![Interactive Map Demo](/landguardian/demo_images/map_interactivity_demo.gif)
- **Real-time Statistics**: Health scores, risk levels, and trend analysis
![Parcel Statistics Demo](/landguardian/demo_images/parcel_statistics_demo.gif)
- **Guided Tour**: Interactive onboarding for new users
![Guided Tour Demo](/landguardian/demo_images/guided_tour_demo.gif)
- **Priority Alerts**: Highlight parcels requiring immediate attention
![Parcels Requiring Attention Highlighted Demo](/landguardian/demo_images/parcels_requiring_attention_highlighted_demo.png)


### 🤖 AI-Powered Predictions
- **Machine Learning Trends**: Scikit-learn powered health score predictions
- **Confidence Scoring**: AI confidence levels for prediction reliability
- **Trend Analysis**: Improving/declining/stable trend detection
- **Historical Data**: 6-month trend visualization with Chart.js

### 📊 Parcel Management
- **Health Scoring**: Weighted algorithm (60% soil + 40% vegetation)
- **Risk Categorization**: Low/Medium/High risk levels with color coding
- **Detailed Analytics**: Individual parcel health trends and recommendations
- **User-Specific Data**: Secure, user-isolated parcel management

### 💡 Smart Recommendations
- **Soil Management**: Compost, testing, and crop rotation suggestions
- **Vegetation Restoration**: Native planting and grazing management
- **Priority Actions**: Risk-based intervention recommendations
- **AI-Enhanced Insights**: ML-powered trend-based advice

### 📤 Export & Reporting
- **CSV Export**: Bulk and individual parcel data export
- **PDF Reports**: Professional formatted reports
- **Data Portability**: Easy data sharing and backup

### 🔐 Security & User Management
- **Flask-Login Integration**: Secure authentication system
- **Password Recovery**: Email-based password reset with rate limiting
- **User Profiles**: Editable profiles with activity tracking
- **Role-Based Access**: Farmer, researcher, and policymaker roles

### ⚙️ User Preferences
- **Map Styles**: Satellite, terrain, and street view options
- **Unit Systems**: Metric/imperial unit preferences
- **Settings Management**: Persistent user preferences

## 🛠️ Technology Stack

### Backend
- **Flask 2.3.3**: Lightweight WSGI web application framework
- **SQLAlchemy 3.0.5**: ORM for database operations
- **Flask-Login**: User session management
- **Flask-Mail**: Email functionality for password recovery

### Frontend
- **Bootstrap 5**: Responsive CSS framework
- **Leaflet.js**: Interactive mapping library
- **Chart.js**: Data visualization
- **Vanilla JavaScript**: Custom interactive features

### AI & Data Science
- **Scikit-learn 1.3.0**: Machine learning for trend prediction
- **NumPy 1.24.3**: Numerical computing
- **ReportLab**: PDF generation

### Testing & Quality
- **pytest**: Comprehensive test suite
- **GitHub Actions**: CI/CD pipeline
- **Coverage.py**: Code coverage reporting

## 🚀 Quick Start

### Prerequisites
- Python 3.11.9
- pip package manager
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/landguardian.git
   cd landguardian
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Open in browser**
   ```
   http://127.0.0.1:5000
   ```

### Configuration

Create a `.env` file with the following variables:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///land_data.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
FLASK_ENV=development
```

## 📁 Project Structure

```
landguardian/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── models.py            # Database models (User, LandParcel)
│   ├── routes.py            # Application routes and API endpoints
│   ├── recommendations.py   # Recommendation engine
│   ├── utils/
│   │   ├── predictor.py     # AI prediction logic
│   │   └── pdf_export.py    # PDF generation utilities
│   ├── templates/           # Jinja2 templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── parcel_detail.html
│   │   └── auth templates...
│   └── static/              # Static assets
│       ├── css/style.css
│       └── js/app.js
├── tests/                   # Test suite
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_routes.py
│   ├── test_utils.py
│   └── test_integration.py
├── config.py                # Configuration classes
├── run.py                   # Development server
├── run_tests.py            # Test runner
├── requirements.txt         # Python dependencies
├── pytest.ini              # Test configuration
├── render.yaml             # Render deployment config
├── runtime.txt             # Python version for deployment
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
└── README.md
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python run_tests.py

# Run with coverage
coverage run -m pytest
coverage report

# Run specific test categories
pytest tests/test_models.py
pytest tests/test_routes.py
pytest tests/test_integration.py
```

## 🚢 Deployment

### Render Deployment

1. **Connect your GitHub repository to Render**
2. **Create a new Web Service**
3. **Configure build settings**:
   - **Runtime**: Python 3.11.9
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:create_app() -w 4 -b 0.0.0.0:$PORT`

4. **Set environment variables** in Render dashboard
5. **Deploy!**

### Environment Variables for Production

```env
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:password@host:port/database
MAIL_SERVER=smtp.your-provider.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@domain.com
MAIL_PASSWORD=your-password
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
FLASK_ENV=production
```

## 📊 Health Scoring Algorithm

Land health scores are calculated using a weighted formula:

```
Health Score = (Soil Quality × 0.6) + (Vegetation Cover × 0.4) × 10
```

**Risk Categories:**
- **Low Risk (Green)**: Score ≥ 70
- **Medium Risk (Yellow)**: Score 30-69
- **High Risk (Red)**: Score < 30

## 🤖 AI Prediction System

The AI system uses linear regression to predict future health trends:

- **Training Data**: Historical health scores over 6 months
- **Prediction Window**: Next month's health score
- **Confidence Scoring**: R² score from regression model
- **Trend Classification**: Improving/Declining/Stable based on prediction vs current score

## 🔒 Security Features

- **Password Hashing**: Werkzeug security for password storage
- **Session Management**: Secure cookies with configurable timeouts
- **Rate Limiting**: Login attempt and password reset throttling
- **CSRF Protection**: Flask-WTF integration
- **Security Headers**: CSP, X-Frame-Options, X-Content-Type-Options

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting PR

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **SDG 15**: Life on Land - United Nations Sustainable Development Goals
- **PLP Academy**: For inspiring and providing the opportunity to work this project
- **Flask Community**: For the excellent web framework
- **Open Source Libraries**: Scikit-learn, Leaflet.js, Bootstrap, and many others
- **Environmental Organizations**: For inspiration and data insights


---

**Built with ❤️ for sustainable land management**
