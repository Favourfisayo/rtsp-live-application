from mongoengine import connect, disconnect
import os

db = None

def init_db(app=None):
    """
    Initialize the database connection using MongoEngine.
    Can accept a Flask app or use environment variables directly.
    """
    global db
    
    if app:
        # Get MongoDB URI from Flask app config
        mongodb_uri = app.config.get('MONGODB_URI') or app.config.get('MONGODB_SETTINGS', {}).get('host')
    else:
        # Get MongoDB URI from environment
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/rtsp_overlay_db')
    
    db = connect(host=mongodb_uri)
    return db

def disconnect_db():
    """Disconnect from MongoDB"""
    disconnect()
