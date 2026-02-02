# import os
# import json
# import base64
# from pathlib import Path
# from datetime import timedelta

# # Optionally load .env if python-dotenv is installed (no hard dependency)
# try:
#     from dotenv import load_dotenv
#     load_dotenv(os.path.join(Path(__file__).resolve().parent.parent, '.env'))
# except Exception:
#     pass

# # Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent

# # SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'your-secret-key-here'

# # SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True

# ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'your-domain.com']

# # Application definition
# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     'rest_framework',
#     'rest_framework.authtoken',
#     'corsheaders',
#     'api',  # Main API app
# ]

# MIDDLEWARE = [
#     'corsheaders.middleware.CorsMiddleware',
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]

# ROOT_URLCONF = 'safeTap.urls'

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]

# WSGI_APPLICATION = 'safeTap.wsgi.application'

# # Database Configuration for PostgreSQL
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'SafeTap',
#         'USER': 'postgres',
#         'PASSWORD': 'munna',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# # Password validation
# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]

# # Internationalization
# LANGUAGE_CODE = 'en-us'
# TIME_ZONE = 'UTC'
# USE_I18N = True
# USE_TZ = True

# # Static files (CSS, JavaScript, Images)
# STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# # Media files
# MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# # Default primary key field type
# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# # Firebase Configuration
# # Try to get Firebase credentials from environment variables
# FIREBASE_CREDENTIALS = None

# # First try JSON string
# firebase_credentials_json = os.environ.get('FIREBASE_CREDENTIALS_JSON', '')
# if firebase_credentials_json:
#     try:
#         FIREBASE_CREDENTIALS = json.loads(firebase_credentials_json)
#         print("Loaded Firebase credentials from JSON string")
#     except Exception as e:
#         print(f"Error parsing Firebase credentials JSON: {str(e)}")
#         FIREBASE_CREDENTIALS = None

# # If JSON didn't work, try base64
# if not FIREBASE_CREDENTIALS:
#     firebase_credentials_base64 = os.environ.get('FIREBASE_CREDENTIALS_BASE64', '')
#     if firebase_credentials_base64:
#         try:
#             decoded = base64.b64decode(firebase_credentials_base64).decode('utf-8')
#             FIREBASE_CREDENTIALS = json.loads(decoded)
#             print("Loaded Firebase credentials from base64 string")
#         except Exception as e:
#             print(f"Error parsing Firebase credentials base64: {str(e)}")
#             FIREBASE_CREDENTIALS = None

# # If still no credentials, try individual environment variables
# if not FIREBASE_CREDENTIALS:
#     FIREBASE_CREDENTIALS = {
#         "type": "service_account",
#         "project_id": os.environ.get('FIREBASE_PROJECT_ID', ''),
#         "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID', ''),
#         "private_key": os.environ.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
#         "client_email": os.environ.get('FIREBASE_CLIENT_EMAIL', ''),
#         "client_id": os.environ.get('FIREBASE_CLIENT_ID', ''),
#         "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#         "token_uri": "https://oauth2.googleapis.com/token",
#         "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#         "client_x509_cert_url": os.environ.get('FIREBASE_CLIENT_X509_CERT_URL', ''),
#         "universe_domain": "googleapis.com"
#     }
#     print("Using individual Firebase environment variables")

# # Ensure private_key has proper newlines
# if FIREBASE_CREDENTIALS and isinstance(FIREBASE_CREDENTIALS, dict):
#     pk = FIREBASE_CREDENTIALS.get('private_key')
#     if pk and isinstance(pk, str) and '\\n' in pk:
#         FIREBASE_CREDENTIALS['private_key'] = pk.replace('\\n', '\n')

# # Email Configuration
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'  # Change based on your email provider
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
# DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@yourdomain.com')

# # Rest Framework Configuration
# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'rest_framework.authentication.TokenAuthentication',
#         'api.firebase_auth.FirebaseAuthentication',  # Add Firebase authentication
#     ],
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.IsAuthenticated',
#     ],
#     'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
#     'PAGE_SIZE': 20,
# }

# # CORS Configuration
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
# ]

# CORS_ALLOW_CREDENTIALS = True

# # Additional settings for better security and performance
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# X_FRAME_OPTIONS = 'DENY'

# # Session configuration
# SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
# SESSION_COOKIE_HTTPONLY = True
# SESSION_COOKIE_SAMESITE = 'Lax'
# SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# # CSRF configuration
# CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS
# CSRF_COOKIE_HTTPONLY = True
# CSRF_COOKIE_SAMESITE = 'Lax'

# # File upload settings
# DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
# FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# # Logging configuration
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
#             'style': '{',
#         },
#         'simple': {
#             'format': '{levelname} {message}',
#             'style': '{',
#         },
#     },
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#             'formatter': 'verbose',
#         },
#         'file': {
#             'class': 'logging.FileHandler',
#             'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
#             'formatter': 'verbose',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['console', 'file'],
#             'level': 'INFO',
#             'propagate': True,
#         },
#         'api': {
#             'handlers': ['console', 'file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
# }

# # Twilio Configuration
# TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
# TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
# TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '')

# # Create logs directory if it doesn't exist
# LOGS_DIR = os.path.join(BASE_DIR, 'logs')
# if not os.path.exists(LOGS_DIR):
#     os.makedirs(LOGS_DIR)


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
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')

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
        'NAME': os.environ.get('DB_NAME', 'SafeTap'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'munna'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
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
# Try to get Firebase credentials from environment variables
FIREBASE_CREDENTIALS = None

# First try JSON string
firebase_credentials_json = os.environ.get('FIREBASE_CREDENTIALS_JSON', '')
if firebase_credentials_json:
    try:
        FIREBASE_CREDENTIALS = json.loads(firebase_credentials_json)
        print("Loaded Firebase credentials from JSON string")
    except Exception as e:
        print(f"Error parsing Firebase credentials JSON: {str(e)}")
        FIREBASE_CREDENTIALS = None

# If JSON didn't work, try base64
if not FIREBASE_CREDENTIALS:
    firebase_credentials_base64 = os.environ.get('FIREBASE_CREDENTIALS_BASE64', '')
    if firebase_credentials_base64:
        try:
            decoded = base64.b64decode(firebase_credentials_base64).decode('utf-8')
            FIREBASE_CREDENTIALS = json.loads(decoded)
            print("Loaded Firebase credentials from base64 string")
        except Exception as e:
            print(f"Error parsing Firebase credentials base64: {str(e)}")
            FIREBASE_CREDENTIALS = None

# If still no credentials, try an on-disk credentials file (firebase-credentials.json)
if not FIREBASE_CREDENTIALS:
    # Allow explicit file path via env var
    firebase_credentials_file = os.environ.get('FIREBASE_CREDENTIALS_FILE', '')
    possible_paths = []
    if firebase_credentials_file:
        possible_paths.append(firebase_credentials_file)
    # Common locations to check
    possible_paths += [
        os.path.join(BASE_DIR, 'firebase-credentials.json'),
        os.path.join(BASE_DIR, 'safeTap', 'firebase-credentials.json'),
        os.path.join(BASE_DIR, 'safeTap', 'api', 'firebase-credentials.json'),
        os.path.join(BASE_DIR, 'safeTap', 'safeTap', 'firebase-credentials.json'),
    ]

    for p in possible_paths:
        try:
            if p and os.path.exists(p):
                with open(p, 'r', encoding='utf-8') as f:
                    FIREBASE_CREDENTIALS = json.load(f)
                print(f"Loaded Firebase credentials from file: {p}")
                break
        except Exception as e:
            print(f"Error reading Firebase credentials file {p}: {str(e)}")
            FIREBASE_CREDENTIALS = None

# If still no credentials, try individual environment variables
if not FIREBASE_CREDENTIALS:
    # Get the private key and properly format it
    private_key = os.environ.get('FIREBASE_PRIVATE_KEY', '')
    if private_key:
        # Remove any leading/trailing whitespace and quotes
        private_key = private_key.strip()
        if private_key.startswith('"') and private_key.endswith('"'):
            private_key = private_key[1:-1]
        
        # Replace literal \n with actual newlines
        private_key = private_key.replace('\\n', '\n')
        # Also handle cases where \n might be double-escaped
        private_key = private_key.replace('\\\\n', '\n')
    
    FIREBASE_CREDENTIALS = {
        "type": "service_account",
        "project_id": os.environ.get('FIREBASE_PROJECT_ID', ''),
        "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID', ''),
        "private_key": private_key,
        "client_email": os.environ.get('FIREBASE_CLIENT_EMAIL', ''),
        "client_id": os.environ.get('FIREBASE_CLIENT_ID', ''),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.environ.get('FIREBASE_CLIENT_X509_CERT_URL', ''),
        "universe_domain": "googleapis.com"
    }
    print("Using individual Firebase environment variables")

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@yourdomain.com')

# Rest Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'api.firebase_auth.FirebaseAuthentication',  # Add Firebase authentication
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

# Additional settings for better security and performance
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Session configuration
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# CSRF configuration
CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# File upload settings
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'api': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '')

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)