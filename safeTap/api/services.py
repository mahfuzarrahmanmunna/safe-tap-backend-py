import random
import string
from django.conf import settings
from .models import UserProfile

# Optional Twilio import - app can run without it
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    Client = None

def generate_verification_code():
    """Generate a 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))

def send_sms_verification(phone_number, verification_code):
    """Send SMS verification code using Twilio"""
    try:
        # Check if Twilio is available
        if not TWILIO_AVAILABLE:
            print("Twilio package not installed. Verification code will be printed to console.")
            print(f"Verification code for {phone_number}: {verification_code}")
            return True
        
        # Initialize Twilio client
        account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', None)
        
        if not all([account_sid, auth_token, from_number]):
            print("Twilio credentials not configured. Check your settings.")
            # For development, just print the code
            print(f"Verification code for {phone_number}: {verification_code}")
            return True
        
        client = Client(account_sid, auth_token)
        
        message = client.messages.create(
            body=f"Your verification code is: {verification_code}",
            from_=from_number,
            to=phone_number
        )
        
        print(f"SMS sent to {phone_number}: {message.sid}")
        return True
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        # For development, just print the code
        print(f"Verification code for {phone_number}: {verification_code}")
        return True  # Return True to continue the flow even if SMS fails

def verify_phone_number(phone_number):
    """Check if phone number is registered"""
    try:
        profile = UserProfile.objects.get(phone=phone_number)
        return True, profile.user
    except UserProfile.DoesNotExist:
        return False, None
