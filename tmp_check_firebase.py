import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','safeTap.settings')
import django
django.setup()
from api.firebase_config import get_firebase_app
app = get_firebase_app()
print('get_firebase_app() ->', app)
