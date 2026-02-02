# api/firebase_config.py
import os
import json
import base64
from django.conf import settings
import firebase_admin
from firebase_admin import credentials, auth

# Global variable to track initialization status
_firebase_initialized = False
_firebase_app = None

# Optional import for credential validation
try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except Exception:
    CRYPTO_AVAILABLE = False


    """
    The function `validate_firebase_credentials` checks the validity of Firebase credentials provided as
    a dictionary, ensuring required fields are present and validating the private key format.
    
    :param creds: The `validate_firebase_credentials` function is designed to validate a dictionary of
    Firebase credentials. The function checks if the credentials dictionary contains certain required
    keys and validates the format of the private key
    :return: The `validate_firebase_credentials` function returns a tuple with two elements. The first
    element is a boolean value indicating whether the credentials are valid (True) or not (False). The
    second element is either None if the credentials are valid, or a string providing a reason for why
    the credentials are not valid.
    """
def validate_firebase_credentials(creds):
    """Validate the credentials dict and return (True, None) or (False, reason).
    This does NOT print or return secrets.
    """
    if not isinstance(creds, dict):
        return False, 'Credentials must be a dict'

    # Basic required fields
    for key in ('type', 'project_id', 'private_key', 'client_email'):
        if not creds.get(key):
            return False, f'Missing required key: {key}'

    # Validate private key format if cryptography is available
    pk = creds.get('private_key')
    if not isinstance(pk, str) or 'PRIVATE KEY' not in pk:
        return False, 'Private key appears malformed or missing header/footer'

    if CRYPTO_AVAILABLE:
        try:
            pem_bytes = pk.encode('utf-8')
            serialization.load_pem_private_key(pem_bytes, password=None, backend=default_backend())
        except Exception as e:
            return False, f'Private key PEM validation failed: {str(e)}'
    else:
        # If cryptography not available, do minimal checks
        if '-----BEGIN PRIVATE KEY-----' not in pk or '-----END PRIVATE KEY-----' not in pk:
            return False, 'Private key missing PEM boundaries'

    return True, None


def get_firebase_app():
    """
    The `get_firebase_app` function initializes a Firebase app using credentials from settings, corrects
    private key formatting, validates credentials, and handles initialization errors.
    :return: The `get_firebase_app` function returns the initialized Firebase app if it was successfully
    initialized or if it was already initialized before. If the Firebase credentials are not found in
    the settings or if there are issues with the credentials (such as validation failure), it will
    return `None`.
    """
    """
    Get or initialize Firebase app
    """
    global _firebase_initialized, _firebase_app
    
    if _firebase_initialized and _firebase_app:
        return _firebase_app
    
    try:
        # Get Firebase credentials from settings
        firebase_credentials = getattr(settings, 'FIREBASE_CREDENTIALS', None)
        
        if not firebase_credentials:
            print("Firebase credentials not found in settings")
            return None
        
        # Create a copy to avoid modifying the original
        creds = firebase_credentials.copy()
        
        # Fix the private key formatting
        if 'private_key' in creds and isinstance(creds['private_key'], str):
            pk = creds['private_key']

            # Remove any leading/trailing whitespace and quotes
            pk = pk.strip()
            if pk.startswith('"') and pk.endswith('"'):
                pk = pk[1:-1]

            # Replace literal \n with actual newlines (handle double-escaped too)
            pk = pk.replace('\\n', '\n')
            pk = pk.replace('\\\\n', '\n')

            # Normalize CRLF to LF
            pk = pk.replace('\r\n', '\n').replace('\r', '\n')

            # Ensure proper PEM boundaries
            if '-----BEGIN PRIVATE KEY-----' not in pk and '-----BEGIN RSA PRIVATE KEY-----' not in pk:
                pk = '-----BEGIN PRIVATE KEY-----\n' + pk
            if '-----END PRIVATE KEY-----' not in pk and '-----END RSA PRIVATE KEY-----' not in pk:
                pk = pk + '\n-----END PRIVATE KEY-----'

            # Ensure the headers/footers are on their own lines and strip trailing spaces per line
            lines = [line.strip() for line in pk.splitlines() if line.strip()]
            # Insert a blank line after BEGIN header for readability if missing
            if lines and lines[0].startswith('-----BEGIN') and len(lines) > 1 and not lines[1].startswith('-----'):
                pass
            pk = '\n'.join(lines)

            creds['private_key'] = pk
            print("Private key formatting corrected")

        # Validate credentials before trying initialization
        valid, reason = validate_firebase_credentials(creds)
        if not valid:
            # Log validation failure but try to initialize anyway as a fallback. Some PEM parsers
            # can be stricter than firebase_admin's own loading; attempt initialization and
            # surface helpful diagnostics if it fails.
            print(f"Firebase credential validation failed: {reason}")
            if 'private_key' in creds:
                print(f"Private key starts with: {creds['private_key'][:50]}...")
                print(f"Private key contains PEM header: {'-----BEGIN PRIVATE KEY-----' in creds['private_key'] or '-----BEGIN RSA PRIVATE KEY-----' in creds['private_key']}")
            print('Attempting to initialize Firebase Admin SDK despite validation warning...')
            try:
                # Try to initialize with the provided credentials even if validation failed
                if not firebase_admin._apps:
                    cred = credentials.Certificate(creds)
                    _firebase_app = firebase_admin.initialize_app(cred)
                else:
                    _firebase_app = firebase_admin.get_app()
                _firebase_initialized = True
                print('Firebase Admin SDK initialized successfully (fallback path)')
                return _firebase_app
            except Exception as e:
                print(f'Fallback initialization failed: {e}')
                import traceback
                traceback.print_exc()
                return None

        # Check if Firebase is already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate(creds)
            _firebase_app = firebase_admin.initialize_app(cred)
        else:
            _firebase_app = firebase_admin.get_app()
        
        _firebase_initialized = True
        print("Firebase Admin SDK initialized successfully")
        return _firebase_app
        
    except Exception as e:
        print(f"Error initializing Firebase: {str(e)}")
        import traceback
        traceback.print_exc()  # This will print the full stack trace
        _firebase_initialized = False
        return None

def is_firebase_available():
    """
    Check if Firebase is available and initialized
    """
    return _firebase_initialized and _firebase_app is not None

def verify_firebase_token(id_token):
    """
    Verify a Firebase ID token and return the decoded token
    """
    app = get_firebase_app()
    if not app:
        print("Firebase not initialized. Cannot verify token.")
        return None
    
    try:
        decoded_token = auth.verify_id_token(id_token, app=app)
        print(f"Successfully verified Firebase token for user: {decoded_token.get('email')}")
        return decoded_token
    except Exception as e:
        print(f"Error verifying Firebase token: {str(e)}")
        return None