import os

class Config:
    """
    Base configuration class for the LandGuardian Flask application.
    """
    SECRET_KEY = os.urandom(24).hex()
    SQLALCHEMY_DATABASE_URI = 'sqlite:///land_data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True

class DevelopmentConfig(Config):
    """
    Development configuration with debugging enabled.
    """
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """
    Production configuration with environment variable support.
    """
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///land_data.db'
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24).hex()