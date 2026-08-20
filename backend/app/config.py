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

# API Settings
API_PREFIX = "/api/v1"
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
