# yourapp/management/commands/clean_duplicate_users.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

class Command(BaseCommand):
    help = 'Clean up duplicate users with the same email'

    def handle(self, *args, **options):
        # Find all emails that have more than one user
        duplicate_emails = User.objects.values('email').annotate(email_count=models.Count('email')).filter(email_count__gt=1)
        
        for email_data in duplicate_emails:
            email = email_data['email']
            users = User.objects.filter(email=email).order_by('date_joined')
            
            self.stdout.write(f"Found {users.count()} users with email {email}")
            
            # Keep the first user (oldest) and delete the rest
            for user in users[1:]:
                self.stdout.write(f"Deleting user {user.username} (ID: {user.id})")
                user.delete()
        
        self.stdout.write(self.style.SUCCESS('Successfully cleaned up duplicate users'))