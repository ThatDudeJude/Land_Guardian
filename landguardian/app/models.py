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

        __table_args__ = (db.Index('idx_parcel_user_id', 'user_id'),)

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

            __table_args__ = (db.Index('idx_user_email', 'email'),)

            id = db.Column(db.Integer, primary_key=True)

            email = db.Column(db.String(120), unique=True, nullable=False)

            password_hash = db.Column(db.String(128), nullable=False)

            name = db.Column(db.String(100), nullable=False)

            organization = db.Column(db.String(100))

            role = db.Column(db.String(20), default='farmer')

            created_at = db.Column(db.DateTime, default=datetime.utcnow)

            last_login = db.Column(db.DateTime)
            total_logins = db.Column(db.Integer, default=0)

            is_active = db.Column(db.Boolean, default=True)
            preferences = db.Column(db.JSON, default=lambda: {
                'units': 'metric',
                'map_style': 'satellite',
                'notifications': {'email': True, 'browser': True}
            })
            reset_token = db.Column(db.String(128))
            reset_token_expires = db.Column(db.DateTime)

            def set_password(self, password):

                self.password_hash = generate_password_hash(password)

            def check_password(self, password):

                return check_password_hash(self.password_hash, password)

            def generate_reset_token(self):
                """
                Generate a secure password reset token with 1-hour expiration.
                """
                import secrets
                from datetime import datetime, timedelta

                self.reset_token = secrets.token_urlsafe(32)
                self.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
                return self.reset_token

            @staticmethod
            def verify_reset_token(token):
                """
                Verify and return user if token is valid and not expired.
                Invalidates token after use.
                """
                from datetime import datetime

                user = User.query.filter_by(reset_token=token).first()
                if user and user.reset_token_expires > datetime.utcnow():
                    user.reset_token = None
                    user.reset_token_expires = None
                    return user
                return None

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