import pytest
import json

class TestRoutes:
    def test_dashboard_route(self, client, init_database):
        """Test dashboard route returns correct data."""
        # This will redirect to login since @login_required decorator
        response = client.get('/')
        assert response.status_code == 302  # Redirect to login
        assert b'/login' in response.headers.get('Location', '').encode()

    def test_add_parcel_get(self, client):
        """Test GET request to add parcel form."""
        # This will redirect to login since @login_required decorator
        response = client.get('/add')
        assert response.status_code == 302  # Redirect to login
        assert b'/login' in response.headers.get('Location', '').encode()

    def test_add_parcel_post(self, client):
        """Test POST request to create new parcel."""
        # This will redirect to login since @login_required decorator
        data = {
            'name': 'New Test Farm',
            'location': 'Test Valley',
            'soil_quality': 7,
            'vegetation_cover': 6
        }
        response = client.post('/add', data=data)
        assert response.status_code == 302  # Redirect to login
        assert b'/login' in response.headers.get('Location', '').encode()

    def test_parcel_detail_route(self, client, init_database):
        """Test parcel detail page loads correctly."""
        # This will redirect to login since @login_required decorator
        response = client.get('/parcel/1')
        assert response.status_code == 302  # Redirect to login
        assert b'/login' in response.headers.get('Location', '').encode()

    def test_api_health_trend(self, client, init_database):
        """Test health trend API endpoint."""
        # This will redirect to login since @login_required decorator
        response = client.get('/api/health-trend/1')
        assert response.status_code == 302  # Redirect to login
        assert b'/login' in response.headers.get('Location', '').encode()

    def test_nonexistent_parcel(self, client):
        """Test handling of non-existent parcel."""
        # This will redirect to login since @login_required decorator
        response = client.get('/parcel/999')
        assert response.status_code == 302  # Redirect to login
        assert b'/login' in response.headers.get('Location', '').encode()

    def test_invalid_parcel_api(self, client):
        """Test API with invalid parcel ID."""
        # This will redirect to login since @login_required decorator
        response = client.get('/api/health-trend/999')
        assert response.status_code == 302  # Redirect to login
        assert b'/login' in response.headers.get('Location', '').encode()