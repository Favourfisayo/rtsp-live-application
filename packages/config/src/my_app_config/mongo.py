import os
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def validate_mongodb_uri(uri: str) -> bool:
    """Validate MongoDB URI format and structure."""
    try:
        if not uri or not isinstance(uri, str):
            return False
        
        # Parse URI
        parsed = urlparse(uri)
        
        # Check scheme
        if parsed.scheme not in ('mongodb', 'mongodb+srv'):
            logger.error(f"Invalid MongoDB scheme: {parsed.scheme}")
            return False
        
        # Check hostname exists
        if not parsed.hostname:
            logger.error("MongoDB URI missing hostname")
            return False
        
        return True
    except Exception as e:
        logger.error(f"MongoDB URI validation error: {e}")
        return False

uri = os.getenv("MONGODB_URI")

if uri:
    if not validate_mongodb_uri(uri):
        logger.warning("Invalid MONGODB_URI, falling back to localhost")
        uri = None

if uri:
    MONGODB_SETTINGS = {
        'host': uri,
        'maxPoolSize': 50,
        'minPoolSize': 10,
        'maxIdleTimeMS': 45000,
        'connectTimeoutMS': 10000,
        'serverSelectionTimeoutMS': 10000,
    }
else:
    MONGODB_SETTINGS = {
        'db': 'my_database',
        'host': 'localhost',
        'port': 27017,
        'maxPoolSize': 50,
        'minPoolSize': 10,
    }
