"""Configuration Management"""
import os
from dotenv import load_dotenv

load_dotenv()

# Application
APP_NAME = "IS- API"
APP_VERSION = "0.1.0"

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/is_logistics"
)

# OR-Tools Configuration
OR_TOOLS_TIME_LIMIT = int(os.getenv("OR_TOOLS_TIME_LIMIT", "30"))  # seconds
OR_TOOLS_LOG_SEARCH = os.getenv("OR_TOOLS_LOG_SEARCH", "false").lower() == "true"

# Google Maps API Configuration
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
GOOGLE_MAPS_DISTANCE_MATRIX_CACHE = os.getenv("GOOGLE_MAPS_DISTANCE_MATRIX_CACHE", "true").lower() == "true"
GOOGLE_MAPS_CACHE_TTL = int(os.getenv("GOOGLE_MAPS_CACHE_TTL", "3600"))  # seconds (1 hour)

# API Settings
API_PREFIX = "/api/v1"
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
