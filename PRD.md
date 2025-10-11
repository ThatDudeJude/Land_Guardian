# 🎯 **Project Requirements Document (PRD) for LandGuardian**

## **Project Overview**
**Project Name:** LandGuardian - Land Degradation Monitoring System  
**Timeline:** 2.5 days  
**Tech Stack:** Flask, SQLite, Bootstrap, Leaflet.js, Chart.js  
**Target:** Hackathon MVP for SDG 15 - Land Degradation  

## **Core Problem Statement**
"Inefficient land restoration planning due to fragmented data and lack of real-time monitoring capabilities, leading to misallocated resources and delayed interventions in combating land degradation."

## **Key Features**

### **MVP Core Features** ✅
1. **Dashboard Overview**
   - Land parcel statistics (total, high-risk, average health)
   - Interactive map visualization
   - Color-coded risk indicators

2. **Parcel Management**
   - Add new land parcels with soil/vegetation data
   - Automatic health scoring (1-100)
   - Risk categorization (Low/Medium/High)

3. **Visualization**
   - Leaflet map with risk-colored markers
   - Progress bars for health scores
   - Trend charts for historical data

4. **Risk Intelligence**
   - AI-like scoring algorithm
   - Automated risk categorization
   - Actionable recommendations

### **Technical Specifications**
- **Backend:** Flask web framework
- **Database:** SQLite with SQLAlchemy ORM
- **Frontend:** Bootstrap 5 + custom CSS
- **Maps:** Leaflet.js with OpenStreetMap
- **Charts:** Chart.js
- **Deployment:** Railway/Heroku ready

## **File Structure**
```
landguardian/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # Database models
│   ├── routes.py                # All application routes
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── add_parcel.html
│   │   └── parcel_detail.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   └── app.js
│       └── images/
├── instance/
│   └── config.py                # Instance-specific config
├── tests/                       # Unit tests
├── requirements.txt
├── run.py                       # Development server
└── config.py                    # Main configuration
```

 