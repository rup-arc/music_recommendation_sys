import pytest
from app import app, load_songs_data

def test_app_creation():
    """Test that Flask app is created successfully"""
    assert app is not None
    assert app.name == 'app'

def test_health_endpoint():
    """Test health endpoint"""
    with app.test_client() as client:
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data

def test_data_loading():
    """Test data loading function"""
    # This will test if data can be loaded
    result = load_songs_data()
    # Should return True if data loads successfully
    assert isinstance(result, bool)

def test_recommend_endpoint():
    """Test recommendation endpoint"""
    with app.test_client() as client:
        # Test with missing mood
        response = client.post('/recommend', json={})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == False

        # Test with mood
        response = client.post('/recommend', json={'mood': 'happy'})
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data