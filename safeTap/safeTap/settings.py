import os
import json
import base64
from pathlib import Path
from datetime import timedelta

# Optionally load .env if python-dotenv is installed (no hard dependency)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(Path(__file__).resolve().parent.parent, '.env'))
except Exception:
    pass

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'your-secret-key-here'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'your-domain.com']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'api',  # Main API app
]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'safeTap.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'safeTap.wsgi.application'

# Database Configuration for PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'SafeTap',
        'USER': 'postgres',
        'PASSWORD': 'munna',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Firebase Configuration
# Prefer setting full service-account JSON in environment for security.
# Supports either:
#  - FIREBASE_CREDENTIALS_JSON  (raw JSON string), or
#  - FIREBASE_CREDENTIALS_BASE64 (base64-encoded JSON)
# Falls back to individual env vars for convenience if those are not provided.
FIREBASE_CREDENTIALS_JSON = os.environ.get('FIREBASE_CREDENTIALS_JSON', '')
FIREBASE_CREDENTIALS_BASE64 = os.environ.get('FIREBASE_CREDENTIALS_BASE64', '')

FIREBASE_CREDENTIALS = None

if FIREBASE_CREDENTIALS_JSON:
    try:
        FIREBASE_CREDENTIALS = json.loads(FIREBASE_CREDENTIALS_JSON)
    except Exception:
        FIREBASE_CREDENTIALS = None

if not FIREBASE_CREDENTIALS and FIREBASE_CREDENTIALS_BASE64:
    try:
        decoded = base64.b64decode(FIREBASE_CREDENTIALS_BASE64).decode('utf-8')
        FIREBASE_CREDENTIALS = json.loads(decoded)
    except Exception:
        FIREBASE_CREDENTIALS = None

# Fall back to older per-key environment variables
if not FIREBASE_CREDENTIALS:
    FIREBASE_CREDENTIALS = {
        "type": "service_account",
        "project_id": os.environ.get('FIREBASE_PROJECT_ID', ''),
        "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID', ''),
        "private_key": os.environ.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
        "client_email": os.environ.get('FIREBASE_CLIENT_EMAIL', ''),
        "client_id": os.environ.get('FIREBASE_CLIENT_ID', ''),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.environ.get('FIREBASE_CLIENT_X509_CERT_URL', ''),
        "universe_domain": "googleapis.com"
    }

# Ensure private_key has proper newlines (it may be provided with escaped \n in env)
if FIREBASE_CREDENTIALS and isinstance(FIREBASE_CREDENTIALS, dict):
    pk = FIREBASE_CREDENTIALS.get('private_key')
    if pk and isinstance(pk, str) and '\\n' in pk:
        FIREBASE_CREDENTIALS['private_key'] = pk.replace('\\n', '\n')

# NOTE: We intentionally removed the file-based setting `FIREBASE_ADMIN_SDK_CREDENTIALS`.
# To migrate: remove `api/firebase-credentials.json` from the repo and set
# `FIREBASE_CREDENTIALS_JSON` (or `FIREBASE_CREDENTIALS_BASE64`) in your .env file.
# Example (in .env):
# FIREBASE_CREDENTIALS_JSON='{"type":"service_account","project_id":"...",...}'
# or for base64:
# FIREBASE_CREDENTIALS_BASE64='<base64 encoded JSON>'

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Change based on your email provider
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@yourdomain.com')

# Rest Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True