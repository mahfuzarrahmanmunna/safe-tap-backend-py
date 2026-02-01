# SafeTap - Water Project Backend API

A comprehensive Django REST API for managing safe drinking water initiatives across Bangladesh. This backend powers the SafeTap water distribution and management platform.

## 🌍 Project Overview

SafeTap is a backend system designed to help manage safe water access across different cities and districts in Bangladesh. It provides features for:

- **Geographic Management**: Track safe water initiatives by Division, District, and Thana (administrative divisions)
- **City Management**: Manage water products, statistics, and promotional slides for each city
- **User Authentication**: Secure user registration and phone-based verification using SMS
- **Product Management**: Display water products with features and pricing
- **Support System**: Generate support links and QR codes for customer service
- **Technical Information**: Showcase water treatment specifications and features

## 🏗️ Project Structure

```
safeTap/
├── manage.py                 # Django management script
├── api/                      # Main API application
│   ├── models.py            # Data models (City, Product, User, etc.)
│   ├── views.py             # API endpoints and viewsets
│   ├── serializers.py       # Data serialization/validation
│   ├── services.py          # Business logic (SMS, verification)
│   ├── urls.py              # API route definitions
│   ├── admin.py             # Django admin configuration
│   ├── permissions.py       # Custom permission classes
│   ├── tests.py             # Unit tests
│   ├── apps.py              # App configuration
│   ├── migrations/          # Database migrations
│   └── __pycache__/         # Python cache
├── safeTap/                 # Main Django project settings
│   ├── settings.py          # Django configuration
│   ├── urls.py              # Main URL routing
│   ├── asgi.py              # ASGI configuration
│   ├── wsgi.py              # WSGI configuration
│   ├── views.py             # Global views
│   └── __pycache__/         # Python cache
└── __pycache__/             # Python cache
```

## 📊 Database Models

### Core Models

**User & Profile**
- `User` - Django's built-in user model
- `UserProfile` - Extended user data with phone verification and support links
  - Phone number and verification status
  - Support link generation
  - QR code generation for support

**Geographic Data**
- `Division` - Bangladesh administrative division (e.g., Dhaka, Chittagong)
- `District` - District within a division (e.g., Narayanganj within Dhaka)
- `Thana` - Sub-district level (e.g., Savar within Narayanganj)

**City & Products**
- `City` - City information with slug for routing
- `CitySlide` - Promotional slides for each city
- `CityStats` - Statistics about water coverage and ratings
- `Product` - Water products available in each city
- `ProductFeature` - Features of water products
- `TechSpec` - Technical specifications and water treatment info

**Content**
- `Post` - Blog posts or news items

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/token/` - Get authentication token
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/send-code/` - Send SMS verification code
- `POST /api/auth/verify-code/` - Verify phone with code
- `POST /api/auth/support-info/` - Get user support information

### Geographic Data
- `GET /api/divisions/` - List all divisions
- `GET /api/districts/` - List all districts
- `GET /api/thanas/` - List all thanas
- `GET /api/bangladesh-data/` - Get complete Bangladesh geographic data

### Cities & Products
- `GET /api/cities/` - List all cities
- `POST /api/cities/bulk/` - Bulk create cities with data
- `GET /api/cities/{slug}/` - Get specific city with slides and products
- `GET /api/tech-specs/` - List technical specifications
- `GET /api/product-features/` - List product features

### Content
- `GET /api/posts/` - List all posts
- `POST /api/posts/` - Create new post (authenticated)

## 🔐 Authentication

The API uses **Token-Based Authentication** (Django REST Framework tokens):

1. User registers via `/api/auth/register/`
2. User receives SMS verification code via `/api/auth/send-code/`
3. User verifies code via `/api/auth/verify-code/`
4. User gets auth token via `/api/auth/token/`
5. Include token in headers: `Authorization: Token <token_key>`

## ⚙️ Key Features

### Phone Verification System
- Generates 6-digit verification codes
- Sends codes via Twilio SMS service
- Tracks verification status per user

### QR Code Generation
- Automatically generates QR codes for support links
- Base64 encodes QR images for API responses
- Displays in Django admin interface

### Geographic Hierarchies
- Organize data by Division → District → Thana
- Support location-based queries
- Enable regional statistics

### City Data Management
- Store city slides for promotional content
- Track city statistics (users, ratings, installations)
- Manage products per city

## 🔧 Setup & Installation

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Installation Steps

```bash
# 1. Navigate to project directory
cd backend

# 2. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install django djangorestframework djangorestframework-simplejwt twilio

# 4. Apply migrations
cd safeTap
python manage.py migrate

# 5. Create superuser (for admin)
python manage.py createsuperuser

# 6. Run development server
python manage.py runserver
```

### Environment Configuration

Create a `.env` file or configure in `settings.py`:

```python
# Twilio Configuration
TWILIO_ACCOUNT_SID = "your_account_sid"
TWILIO_AUTH_TOKEN = "your_auth_token"
TWILIO_PHONE_NUMBER = "your_twilio_number"

# Django Configuration
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

## 📦 Dependencies

- **Django** - Web framework
- **Django REST Framework** - REST API toolkit
- **djangorestframework-simplejwt** - JWT authentication
- **twilio** - SMS service integration
- **qrcode** - QR code generation
- **Pillow** - Image processing

## 🧪 Testing

Run tests with:

```bash
cd safeTap
python manage.py test api
```

## 👨‍💻 Development

### Adding New Features

1. **Create Model** - Define in `api/models.py`
2. **Create Serializer** - Define in `api/serializers.py`
3. **Create ViewSet** - Define in `api/views.py`
4. **Create Migration** - `python manage.py makemigrations`
5. **Apply Migration** - `python manage.py migrate`
6. **Register URL** - Add to router in `api/urls.py`

### Database Migrations

```bash
# Create migrations for changes
python manage.py makemigrations

# View migration SQL
python manage.py sqlmigrate api 0001

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

## 📝 Admin Interface

Access Django admin at `http://localhost:8000/admin`

- Create and edit geographic data (Divisions, Districts, Thanas)
- Manage cities and their products
- View user profiles and verification status
- Preview generated QR codes
- Manage technical specifications

## 🚀 Deployment

For production deployment:

1. Set `DEBUG = False` in settings.py
2. Configure allowed hosts
3. Use production database (PostgreSQL recommended)
4. Configure static files and media serving
5. Use production WSGI server (Gunicorn, uWSGI)
6. Set up SSL/TLS certificates
7. Configure environment variables securely

## 📞 Support System

Users receive:
- Unique support link: `https://yourapp.com/support/{unique_id}`
- QR code containing the support link
- Displayed in their profile

## 🔍 API Response Examples

### Register User
```json
POST /api/auth/register/
{
  "username": "john_doe",
  "password": "secure_password",
  "email": "john@example.com",
  "phone": "+8801700000000"
}
```

### Get City Data
```json
GET /api/cities/dhaka/
{
  "id": 1,
  "name": "Dhaka",
  "slug": "dhaka",
  "slides": [...],
  "stats": {...},
  "products": [...]
}
```

## 📋 License

This project is part of the SafeTap water initiative.

## 🤝 Contributing

Follow Django and DRF best practices:
- Write tests for new features
- Use meaningful commit messages
- Keep models normalized
- Document API endpoints
- Maintain consistent code style

## ⚠️ Important Notes

- Phone numbers must be in international format (e.g., +8801700000000)
- Twilio credentials are required for SMS functionality
- QR codes are generated and stored as base64 in database
- User profiles are auto-created when users register

---

**Last Updated**: January 2026  
**Version**: 1.0
