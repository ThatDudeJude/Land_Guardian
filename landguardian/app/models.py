from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = None

def _define_models():
    global db
    class LandParcel(db.Model):
        """
        Model representing a land parcel in the LandGuardian system.
        """
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        name = db.Column(db.String(100), nullable=False)
        location = db.Column(db.String(100), nullable=False)
        latitude = db.Column(db.Float, nullable=True)
        longitude = db.Column(db.Float, nullable=True)
        soil_quality = db.Column(db.Integer, nullable=False)
        vegetation_cover = db.Column(db.Integer, nullable=False)
        health_score = db.Column(db.Integer, nullable=False)
        risk_level = db.Column(db.String(20), nullable=False)
        risk_label = db.Column(db.String(50), nullable=False)
        risk_color = db.Column(db.String(20), nullable=False)
        last_updated = db.Column(db.DateTime, default=datetime.utcnow)

        user = db.relationship('User', backref=db.backref('parcels', lazy=True))

        def __repr__(self):
            return f'<LandParcel {self.name}>'

        @classmethod
        def calculate_health_score(cls, soil, vegetation):
            """
            Calculate health score from soil quality and vegetation cover using weighted formula.

            Args:
                soil (int): Soil quality score (1-10)
                vegetation (int): Vegetation cover score (1-10)

            Returns:
                int: Health score (0-100)
            """
            return int((soil * 0.6 + vegetation * 0.4) * 10)

        @classmethod
        def get_risk_category(cls, score):
            """
            Get risk category based on health score.

            Args:
                score (int): Health score (0-100)

            Returns:
                tuple: (risk_level, risk_label, risk_color)
            """
            if score < 30:
                return 'High', 'High Risk', 'red'
            elif score < 70:
                return 'Medium', 'Medium Risk', 'yellow'
            else:
                return 'Low', 'Low Risk', 'green'

        class User(db.Model):

            __tablename__ = 'user'

            id = db.Column(db.Integer, primary_key=True)

            email = db.Column(db.String(120), unique=True, nullable=False)

            password_hash = db.Column(db.String(128), nullable=False)

            name = db.Column(db.String(100), nullable=False)

            organization = db.Column(db.String(100))

            role = db.Column(db.String(20), default='farmer')

            created_at = db.Column(db.DateTime, default=datetime.utcnow)

            last_login = db.Column(db.DateTime)

            is_active = db.Column(db.Boolean, default=True)

            def set_password(self, password):

                self.password_hash = generate_password_hash(password)

            def check_password(self, password):

                return check_password_hash(self.password_hash, password)

            def get_id(self):

                return str(self.id)

            @property

            def is_authenticated(self):

                return True

            @property

            def is_active(self):

                return self.is_active

            @property

            def is_anonymous(self):

                return False

        globals()['User'] = User

    globals()['LandParcel'] = LandParcel