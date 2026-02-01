import os
import django

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import UserProfile

def setup_admin_and_cleanup():
    """Set up admin user and delete all other users"""
    
    # Get the admin user
    try:
        admin_user = User.objects.get(id=4747)
        print(f"Found admin user: {admin_user.email}")
    except User.DoesNotExist:
        print("Admin user not found!")
        return
    
    # Set admin role
    profile, created = UserProfile.objects.get_or_create(
        user=admin_user,
        defaults={'role': 'admin'}
    )
    
    profile.role = 'admin'
    profile.save()
    
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()
    
    print(f"Admin user {admin_user.email} is now set as admin!")
    
    # Delete all other users
    other_users = User.objects.exclude(id=4747)
    count = other_users.count()
    
    # Delete profiles first
    UserProfile.objects.exclude(user=admin_user).delete()
    
    # Delete users
    other_users.delete()
    
    print(f"Deleted {count} other users")
    
    # Verify
    print(f"Users remaining: {User.objects.count()}")
    print(f"Profiles remaining: {UserProfile.objects.count()}")

if __name__ == '__main__':
    setup_admin_and_cleanup()