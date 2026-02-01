import os
import json
import uuid
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


# Optional Firebase Admin SDK import - app can run without it
try:
    import firebase_admin
    from firebase_admin import credentials, auth
    FIREBASE_ADMIN_AVAILABLE = True
except ImportError:
    FIREBASE_ADMIN_AVAILABLE = False
    firebase_admin = None
    credentials = None
    auth = None

# Initialize Firebase Admin SDK
firebase_initialized = False
if FIREBASE_ADMIN_AVAILABLE:
    try:
        # Prefer an in-memory credentials dict provided via settings (loaded from env)
        firebase_credentials = getattr(settings, 'FIREBASE_CREDENTIALS', None)
        firebase_credentials_path = getattr(settings, 'FIREBASE_ADMIN_SDK_CREDENTIALS', None)

        initialized = False

        # If a credentials dict is provided, use it directly (ensure private key looks valid)
        if firebase_credentials and isinstance(firebase_credentials, dict):
            pk = firebase_credentials.get('private_key', '')
            if pk and 'BEGIN PRIVATE KEY' in pk:
                if not firebase_admin._apps:
                    cred = credentials.Certificate(firebase_credentials)
                    firebase_admin.initialize_app(cred)
                firebase_initialized = True
                initialized = True
                print("Firebase Admin SDK initialized successfully from dict credentials")
            else:
                print("Firebase credentials provided via env appear invalid or missing private key; skipping initialization.")

        # If the setting points to a file path (back-compat/fallback)
        if not initialized and firebase_credentials_path and os.path.exists(firebase_credentials_path):
            if not firebase_admin._apps:
                cred = credentials.Certificate(firebase_credentials_path)
                firebase_admin.initialize_app(cred)
            firebase_initialized = True
            initialized = True
            print("Firebase Admin SDK initialized successfully from credentials file")

        if not initialized:
            print("Firebase credentials not found in settings; Firebase authentication will not work.")
    except Exception as e:
        print(f"Error initializing Firebase: {str(e)}")
        firebase_initialized = False
else:
    print("Firebase Admin SDK package not installed. Firebase authentication will not work.")

def verify_firebase_token(id_token):
    """Verify a Firebase ID token and return the decoded token"""
    if not firebase_initialized or not FIREBASE_ADMIN_AVAILABLE:
        print("Firebase not initialized. Cannot verify token.")
        return None
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        print(f"Successfully verified Firebase token for user: {decoded_token.get('email')}")
        return decoded_token
    except Exception as e:
        print(f"Error verifying Firebase token: {str(e)}")
        return None

def get_or_create_user(firebase_uid, email, display_name=None, photo_url=None):
    """
    Get an existing user or create a new one based on Firebase UID
    """
    try:
        # Import here to avoid circular imports
        from django.contrib.auth.models import User
        from .models import UserProfile
        
        print(f"Getting or creating user for Firebase UID: {firebase_uid}, Email: {email}")
        
        # First, try to find an existing user by Firebase UID
        try:
            profile = UserProfile.objects.get(firebase_uid=firebase_uid)
            print(f"Found existing user by Firebase UID: {profile.user.username}")
            return profile.user
        except UserProfile.DoesNotExist:
            print("No existing user found by Firebase UID")
        
        # If not found by Firebase UID, try to find by email
        try:
            user = User.objects.get(email=email)
            print(f"Found existing user by email: {user.username}")
            
            # Check if this user already has a profile
            try:
                profile = UserProfile.objects.get(user=user)
                # Update the existing profile with Firebase UID if it's not set
                if not profile.firebase_uid:
                    profile.firebase_uid = firebase_uid
                    profile.save()
                    print(f"Updated existing profile with Firebase UID")
                return user
            except UserProfile.DoesNotExist:
                # Create profile if it doesn't exist
                profile = UserProfile.objects.create(user=user, firebase_uid=firebase_uid, role='customer')
                print(f"Created new profile for existing user")
                return user
        except User.DoesNotExist:
            print("No existing user found by email")
        
        # If user doesn't exist, create a new one
        # Generate a unique username from email
        username = email.split('@')[0]
        original_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1
        
        # Split display name into first and last name
        first_name = ""
        last_name = ""
        if display_name:
            name_parts = display_name.split(" ", 1)
            first_name = name_parts[0]
            if len(name_parts) > 1:
                last_name = name_parts[1]
        
        # Create the user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=str(uuid.uuid4())[:8],  # Random password, won't be used for Firebase auth
            first_name=first_name,
            last_name=last_name
        )
        
        print(f"Created new user: {user.username}")
        
        # Create the user profile with Firebase UID
        profile = UserProfile.objects.create(
            user=user,
            firebase_uid=firebase_uid,
            role='customer'
        )
        print(f"Created new profile for new user")
        
        return user
        
    except Exception as e:
        print(f"Error getting or creating user: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

class FirebaseAuthentication(BaseAuthentication):
    """
    Custom authentication class for Firebase tokens
    """
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return None
            
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Verify the Firebase token
        decoded_token = verify_firebase_token(token)
        if not decoded_token:
            return None
            
        # Get user info from token
        firebase_uid = decoded_token.get('uid')
        email = decoded_token.get('email')
        
        # Get user from email
        try:
            user = User.objects.get(email=email)
            return (user, None)  # Return user and auth (None for Firebase)
        except User.DoesNotExist:
            # If user doesn't exist, try to create them
            user = get_or_create_user(firebase_uid, email, decoded_token.get('name'))
            if user:
                return (user, None)
            else:
                raise AuthenticationFailed('Failed to authenticate user')
