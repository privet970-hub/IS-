"""Tests for Google Maps Service"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.maps_service import MapsService
from app.utils.cache import DistanceMatrixCache


class TestMapsService:
    """Test Google Maps service"""
    
    @pytest.fixture
    def maps_service(self):
        """Create MapsService instance for testing"""
        return MapsService(api_key="test_api_key")
    
    def test_haversine_distance_calculation(self, maps_service):
        """Test Haversine distance calculation"""
        # Seoul to Busan approximately
        origin = (37.5665, 126.9780)  # Seoul
        destination = (35.1796, 129.0756)  # Busan
        
        distance = maps_service._get_haversine_distance(origin, destination)
        
        # Distance should be approximately 325 km = 325000 meters
        assert 320000 < distance < 330000
    
    def test_haversine_same_point(self, maps_service):
        """Test Haversine distance for same point"""
        point = (37.5665, 126.9780)
        distance = maps_service._get_haversine_distance(point, point)
        assert distance == 0
    
    def test_haversine_distance_matrix(self, maps_service):
        """Test Haversine distance matrix calculation"""
        locations = [
            (37.5665, 126.9780),  # Seoul
            (37.4979, 127.0276),  # Seongnam
            (35.1796, 129.0756),  # Busan
        ]
        
        matrix = maps_service._get_haversine_distance_matrix(locations, locations)
        
        assert len(matrix) == 3
        assert len(matrix[0]) == 3
        assert matrix[0][0] == 0  # Same point
        assert matrix[0][1] > 0   # Different points
        assert matrix[1][0] > 0   # Symmetric
    
    @patch('googlemaps.Client')
    def test_get_distance_and_duration_with_api(self, mock_client_class, maps_service):
        """Test getting distance and duration from Google Maps API"""
        # Mock the client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        maps_service.client = mock_client
        
        # Mock API response
        mock_client.distance_matrix.return_value = {
            "status": "OK",
            "rows": [
                {
                    "elements": [
                        {
                            "status": "OK",
                            "distance": {"value": 25000},  # 25 km
                            "duration": {"value": 1500},   # 25 minutes
                        }
                    ]
                }
            ]
        }
        
        origin = (37.5665, 126.9780)
        destination = (37.4979, 127.0276)
        
        result = maps_service.get_distance_and_duration(origin, destination)
        
        assert result is not None
        assert result["distance"] == 25000
        assert result["duration"] == 1500
    
    @patch('googlemaps.Client')
    def test_get_distance_matrix_with_api(self, mock_client_class, maps_service):
        """Test getting distance matrix from Google Maps API"""
        # Mock the client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        maps_service.client = mock_client
        
        # Mock API response
        mock_client.distance_matrix.return_value = {
            "status": "OK",
            "rows": [
                {
                    "elements": [
                        {"status": "OK", "distance": {"value": 0}},
                        {"status": "OK", "distance": {"value": 25000}},
                    ]
                },
                {
                    "elements": [
                        {"status": "OK", "distance": {"value": 25000}},
                        {"status": "OK", "distance": {"value": 0}},
                    ]
                }
            ]
        }
        
        origins = [(37.5665, 126.9780), (37.4979, 127.0276)]
        destinations = [(37.5665, 126.9780), (37.4979, 127.0276)]
        
        matrix = maps_service.get_distance_matrix(origins, destinations)
        
        assert len(matrix) == 2
        assert len(matrix[0]) == 2
        assert matrix[0][0] == 0
        assert matrix[0][1] == 25000
    
    def test_get_distance_and_duration_fallback(self, maps_service):
        """Test fallback to Haversine when API is unavailable"""
        # Set client to None to trigger fallback
        maps_service.client = None
        
        origin = (37.5665, 126.9780)
        destination = (37.4979, 127.0276)
        
        result = maps_service.get_distance_and_duration(origin, destination)
        
        assert result is not None
        assert "distance" in result
        assert "duration" in result
        assert result["distance"] > 0
    
    def test_cache_functionality(self, maps_service):
        """Test that caching works"""
        origin = (37.5665, 126.9780)
        destination = (37.4979, 127.0276)
        
        # Set client to None to force Haversine calculation
        maps_service.client = None
        
        # First call
        result1 = maps_service.get_distance_and_duration(origin, destination)
        
        # Second call should use cache
        result2 = maps_service.get_distance_and_duration(origin, destination)
        
        assert result1 == result2


class TestDistanceMatrixCache:
    """Test distance matrix cache"""
    
    @pytest.fixture
    def cache(self):
        """Create cache instance"""
        return DistanceMatrixCache(max_size=10, ttl_seconds=3600)
    
    def test_cache_set_and_get(self, cache):
        """Test setting and getting cache values"""
        origin = (37.5665, 126.9780)
        destination = (37.4979, 127.0276)
        value = {"distance": 25000, "duration": 1500}
        
        cache.set(origin, destination, value)
        cached = cache.get(origin, destination)
        
        assert cached == value
    
    def test_cache_miss(self, cache):
        """Test cache miss"""
        origin = (37.5665, 126.9780)
        destination = (37.4979, 127.0276)
        
        result = cache.get(origin, destination)
        assert result is None
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full"""
        cache = DistanceMatrixCache(max_size=2, ttl_seconds=3600)
        
        origin1 = (37.5665, 126.9780)
        dest1 = (37.4979, 127.0276)
        
        origin2 = (35.1796, 129.0756)
        dest2 = (36.0000, 128.0000)
        
        origin3 = (34.0000, 127.0000)
        dest3 = (34.5000, 127.5000)
        
        cache.set(origin1, dest1, {"distance": 1000})
        cache.set(origin2, dest2, {"distance": 2000})
        cache.set(origin3, dest3, {"distance": 3000})
        
        # First entry should be evicted
        assert cache.get(origin1, dest1) is None
        assert cache.get(origin2, dest2) is not None
        assert cache.get(origin3, dest3) is not None
    
    def test_cache_clear(self, cache):
        """Test clearing cache"""
        origin = (37.5665, 126.9780)
        destination = (37.4979, 127.0276)
        
        cache.set(origin, destination, {"distance": 25000})
        assert cache.size() == 1
        
        cache.clear()
        assert cache.size() == 0
        assert cache.get(origin, destination) is None
