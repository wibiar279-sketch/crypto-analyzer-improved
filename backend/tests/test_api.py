"""
Sample tests for the API endpoints.
"""
import pytest
from src.main import create_app
from src.models import db


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'service' in data


def test_index(client):
    """Test root endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'running'
    assert 'version' in data


def test_api_docs(client):
    """Test API documentation endpoint."""
    response = client.get('/api/v1/docs')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'endpoints' in data


def test_get_pairs(client):
    """Test get trading pairs endpoint."""
    response = client.get('/api/v1/pairs')
    assert response.status_code in [200, 503]  # 503 if Indodax API unavailable
    
    if response.status_code == 200:
        data = response.get_json()
        assert 'success' in data


def test_invalid_endpoint(client):
    """Test invalid endpoint returns 404."""
    response = client.get('/api/v1/invalid_endpoint')
    assert response.status_code == 404
    
    data = response.get_json()
    assert data['success'] is False


def test_invalid_pair_id(client):
    """Test invalid pair ID validation."""
    response = client.get('/api/v1/ticker/invalid!')
    assert response.status_code == 400
    
    data = response.get_json()
    assert data['success'] is False
    assert 'error' in data
