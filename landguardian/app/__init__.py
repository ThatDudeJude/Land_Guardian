from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    """
    Application factory function for creating Flask app instances.

    This function implements the Flask application factory pattern, allowing
    for multiple app instances with different configurations, which is useful
    for testing and running different environments.

    Args:
        config_class: Configuration class to use for the app (default: Config).

    Returns:
        Flask app instance configured with the specified config class.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    # Register blueprints here (to be implemented later)

    return app