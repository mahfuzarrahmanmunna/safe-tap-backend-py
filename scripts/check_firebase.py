import sys
sys.path.insert(0, r'e:/water-project/backend/safeTap')
from api.firebase_config import get_firebase_app, is_firebase_available
app = get_firebase_app()
print('is_firebase_available:', is_firebase_available())
