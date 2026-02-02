# api/firebase_auth.py
import os
import json
import uuid
from django.conf import settings
from .firebase_config import get_firebase_app, is_firebase_available, verify_firebase_token
from .firebase_config import get_firebase_app
from .firebase_config import is_firebase_available


# Initialize Firebase Admin SDK
firebase_initialized = False
firebase_app = get_firebase_app()

if is_firebase_available():
    firebase_initialized = True
    print("Firebase Admin SDK is available")
else:
    print("Firebase Admin SDK is not available. Firebase authentication will not work.")

def get_or_create_user(firebase_uid, email, display_name=None, photo_url=None):
    """
    Get an existing user or create a new one based on Firebase UID.
    This function is resilient to missing email or display name in the decoded Firebase token.
    """
    try:
        # Import here to avoid circular imports
        from django.contrib.auth.models import User
        from .models import UserProfile
        from django.db import IntegrityError

        print(f"Getting or creating user for Firebase UID: {firebase_uid}, Email: {email}")

        # 1) Try to find by Firebase UID
        try:
            profile = UserProfile.objects.get(firebase_uid=firebase_uid)
            print(f"Found existing user by Firebase UID: {profile.user.username}")
            return profile.user
        except UserProfile.DoesNotExist:
            print("No existing user found by Firebase UID")

        # 2) Try to find by email when available
        if email:
            try:
                user = User.objects.get(email=email)
                print(f"Found existing user by email: {user.username}")

                # Ensure profile exists and is linked
                profile, created = UserProfile.objects.get_or_create(user=user)
                if not profile.firebase_uid:
                    profile.firebase_uid = firebase_uid
                    profile.save()
                    print("Updated existing profile with Firebase UID")
                return user
            except User.DoesNotExist:
                print("No existing user found by email")

        # 3) Create a new user when not found
        # Choose a safe username source: email -> display_name -> firebase uid
        if email:
            base_username = email.split('@')[0]
        elif display_name:
            # sanitize display_name to a safe username (alphanumeric and underscores)
            base_username = ''.join([c if c.isalnum() else '_' for c in display_name]).strip('_')
            if not base_username:
                base_username = f'user_{firebase_uid[:8]}'
        else:
            base_username = f'user_{firebase_uid[:8]}'

        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # Split display name into first and last name if provided
        first_name = ""
        last_name = ""
        if display_name:
            name_parts = display_name.split(" ", 1)
            first_name = name_parts[0]
            if len(name_parts) > 1:
                last_name = name_parts[1]

        # Email might be None; Django accepts blank email if not required
        safe_email = email if email else ''

        try:
            user = User.objects.create_user(
                username=username,
                email=safe_email,
                password=str(uuid.uuid4())[:12],  # Random password, won't be used for Firebase auth
                first_name=first_name,
                last_name=last_name
            )
        except IntegrityError as ie:
            # Unlikely due to the username loop, but handle defensively
            print(f"IntegrityError creating user {username}: {ie}")
            # fallback to a uuid username
            username = f"u_{uuid.uuid4().hex[:8]}"
            user = User.objects.create_user(username=username, email=safe_email, password=str(uuid.uuid4())[:12])

        print(f"Created new user: {user.username}")

        # Create or update the user profile with Firebase UID
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.firebase_uid = firebase_uid
        if not getattr(profile, 'role', None):
            profile.role = 'customer'
        profile.save()
        print(f"Created/updated profile for new user")

        return user

    except Exception as e:
        print(f"Error getting or creating user: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# Add this to your existing firebase_auth.py file
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User

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
            
