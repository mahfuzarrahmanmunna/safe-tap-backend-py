import os
import json
import firebase_admin
from firebase_admin import credentials
from django.conf import settings

# Global variable to track initialization
_firebase_app = None
_firebase_initialized = False
_initialization_error = None

def initialize_firebase():
    """
    Initialize Firebase Admin SDK with proper error handling
    """
    global _firebase_app, _firebase_initialized, _initialization_error
    
    # Return if already initialized
    if _firebase_initialized and _firebase_app:
        return _firebase_app
    
    try:
        # Get Firebase credentials from settings
        firebase_credentials = getattr(settings, 'FIREBASE_CREDENTIALS', None)
        
        if not firebase_credentials:
            _initialization_error = "Firebase credentials not found in settings"
            print(f"ERROR: {_initialization_error}")
            return None
        
        # Check if Firebase is already initialized
        if not firebase_admin._apps:
            # Create credentials object
            cred = credentials.Certificate(firebase_credentials)
            
            # Initialize Firebase
            _firebase_app = firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized successfully")
        else:
            _firebase_app = firebase_admin.get_app()
            print("Firebase Admin SDK already initialized")
        
        _firebase_initialized = True
        _initialization_error = None
        return _firebase_app
        
    except Exception as e:
        _initialization_error = str(e)
        print(f"ERROR initializing Firebase: {_initialization_error}")
        _firebase_initialized = False
        return None

def get_firebase_app():
    """
    Get the Firebase app instance
    """
    if not _firebase_initialized:
        return initialize_firebase()
    return _firebase_app

def is_firebase_available():
    """
    Check if Firebase is available and initialized
    """
    return _firebase_initialized and _firebase_app is not None

def get_initialization_error():
    """
    Get the Firebase initialization error message
    """
    return _initialization_error

# Initialize Firebase when the module is imported
initialize_firebase()