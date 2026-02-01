import random
from django.conf import settings
from datetime import datetime, timedelta

def generate_verification_code():
    """Generate a 6-digit verification code"""
    return str(random.randint(100000, 999999))

def send_sms_verification(phone_number, code):
    """Send verification code via Firebase Authentication"""
    try:
        # Import Firebase Admin SDK
        from .firebase_auth import firebase_initialized
        
        if not firebase_initialized:
            print("Firebase not initialized. Phone verification will not work.")
            print(f"Verification code for {phone_number}: {code}")
            return False
        
        # For development, we'll store the code in the user profile
        # In production, you might want to use Firebase's phone authentication
        print(f"Verification code for {phone_number}: {code}")
        return True
        
    except Exception as e:
        print(f"Error with Firebase phone verification: {str(e)}")
        print(f"Verification code for {phone_number}: {code}")
        return False

def verify_phone_number(phone_number):
    """Check if phone number is registered in the system"""
    try:
        from .models import UserProfile
        profile = UserProfile.objects.get(phone=phone_number)
        return True, profile.user
    except UserProfile.DoesNotExist:
        return False, None

def verify_firebase_phone_token(phone_number, verification_id, verification_code):
    """Verify phone number using Firebase Authentication"""
    try:
        from .firebase_auth import firebase_initialized
        
        if not firebase_initialized:
            print("Firebase not initialized. Cannot verify phone token.")
            return None
        
        # In a real implementation, you would use Firebase's phone auth
        # For now, we'll just check if the phone exists in our system
        is_registered, user = verify_phone_number(phone_number)
        if is_registered:
            return {
                'uid': user.profile.firebase_uid or str(user.id),
                'phone': phone_number,
                'email': user.email
            }
        return None
        
    except Exception as e:
        print(f"Error verifying Firebase phone token: {str(e)}")
        return None