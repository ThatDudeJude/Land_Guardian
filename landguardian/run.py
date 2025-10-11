from app import create_app
from config import DevelopmentConfig

if __name__ == '__main__':
    # Create the Flask app instance with development configuration
    app = create_app(DevelopmentConfig)
    # Run the development server with debug mode enabled on port 5000
    app.run(debug=True, port=5000)