from django.http import HttpResponse
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError
from datetime import datetime, timedelta

from .models import Post, City, TechSpec, Division, District, Thana, ProductFeature, UserProfile, WorkAssignment, WorkCategory, AssignmentHistory
from .serializers import (
    CitySerializer, CitySlideSerializer, CityStatsSerializer, 
    ProductSerializer, TechSpecSerializer, PostSerializer,
    DivisionSerializer, DistrictSerializer, ThanaSerializer, BangladeshDataSerializer, 
    ProductFeatureSerializer, 
    PhoneVerificationSerializer,
    UserRegistrationSerializer,
    CodeVerificationSerializer, PhoneLoginSerializer, LoginSerializer,
    FirebaseTokenSerializer, FirebaseRegistrationSerializer, WorkAssignmentSerializer, WorkAssignmentCreateSerializer,
    WorkCategorySerializer, TechnicianListSerializer, WorkAssignment, AssignmentHistory, AssignmentHistorySerializer,
    ServiceRequest, ServiceRequestSerializer, ServiceRequestCreateSerializer, ServiceRequestImage, ServiceRequestVideo,
    UserListSerializer
)
from .services import generate_verification_code, send_sms_verification, verify_phone_number
from .firebase_auth import verify_firebase_token, get_or_create_user, FirebaseAuthentication
import uuid
import qrcode
from io import BytesIO
import base64

def home(request):
    return HttpResponse('hello api')

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    Simple test endpoint to verify API connection
    """
    return Response({
        "status": "success",
        "message": "API is working correctly",
        "endpoints": {
            "cities": "/api/cities/",
            "tech-specs": "/api/tech-specs/",
            "divisions": "/api/divisions/",
            "districts": "/api/districts/",
            "thanas": "/api/thanas/",
            "product-features": "/api/product-features/",
            "auth": {
                "register": "/api/auth/register/",
                "login": "/api/auth/login/",
                "token": "/api/auth/token/",
                "verify-email": "/api/auth/verify-email/",
                "send-email": "/api/auth/send-email/",
                "me": "/api/auth/me/",
                "support": "/api/auth/support/",
                "users": "/api/auth/users/",
                "users_firebase": "/api/auth/users/firebase/",
                "phone": {
                    "send-code": "/api/auth/phone/send-code/",
                    "verify": "/api/auth/phone/verify/",
                    "login": "/api/auth/phone/login/"
                },
                "firebase": {
                    "login": "/api/auth/firebase/login/",
                    "register": "/api/auth/firebase/register/"
                }
            }
        }
    })

@api_view(['GET', 'POST'])
def post_list(request):
    """
    List all posts, or create a new post.
    """
    if request.method == 'GET':
        posts = Post.objects.all().order_by('-created_at')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            # This will fail if no user is logged in. Handle this.
            if request.user.is_authenticated:
                serializer.save(author=request.user)
            else:
                # For now, let's not save if no user is authenticated
                return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

# New PIN-based authentication view
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Login user with email and PIN"""
    try:
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            pin = serializer.validated_data['pin']
            bypass_email_verification = serializer.validated_data.get('bypass_email_verification', False)
            
            try:
                # Get user by email
                user = User.objects.get(email=email)
                
                try:
                    profile = user.profile
                except UserProfile.DoesNotExist:
                    return Response({
                        'error': 'User profile not found'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                # Check if PIN matches
                if profile.pin != pin:
                    return Response({
                        'error': 'Invalid PIN'
                    }, status=status.HTTP_401_UNAUTHORIZED)
                
                # Only check email verification if not in development mode
                if not bypass_email_verification and not profile.is_email_verified:
                    return Response({
                        'error': 'Email not verified. Please verify your email first.',
                        'verification_required': True
                    }, status=status.HTTP_401_UNAUTHORIZED)
                
                # Generate token for Django API access
                token, created = Token.objects.get_or_create(user=user)
                
                return Response({
                    'message': 'Login successful',
                    'token': token.key,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'phone': profile.phone,
                        'role': profile.role,
                        'qr_code': profile.qr_code
                    }
                })
                
            except User.DoesNotExist:
                return Response({
                    'error': 'User with this email does not exist'
                }, status=status.HTTP_404_NOT_FOUND)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_serializer_context(self): 
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    @action(detail=False, methods=['get', 'post'])
    def bulk(self, request):
        if request.method == 'GET':
            cities = City.objects.all()
            serializer = CitySerializer(cities, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            cities_data = request.data.get('cities', [])
            
            if not cities_data:
                return Response(
                    {"error": "No cities data provided"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            created_cities = []
            errors = []
            
            for city_data in cities_data:
                try:
                    city_serializer = CitySerializer(data={
                        'name': city_data.get('name'),
                        'slug': city_data.get('slug', city_data.get('name', '').lower())
                    })
                    
                    if city_serializer.is_valid():
                        city = city_serializer.save()
                        
                        # Create slides
                        slides_data = city_data.get('slides', [])
                        for slide_data in slides_data:
                            slide_serializer = CitySlideSerializer(data={
                                **slide_data,
                                'city': city.id
                            })
                            if slide_serializer.is_valid():
                                slide_serializer.save()
                            else:
                                errors.append({
                                    'city': city.name,
                                    'slide': slide_data.get('title', 'Unknown'),
                                    'errors': slide_serializer.errors
                                })
                        
                        # Create stats
                        stats_data = city_data.get('stats')
                        if stats_data:
                            stats_serializer = CityStatsSerializer(data={
                                **stats_data,
                                'city': city.id
                            })
                            if stats_serializer.is_valid():
                                stats_serializer.save()
                            else:
                                errors.append({
                                    'city': city.name,
                                    'stats': stats_serializer.errors
                                })
                        
                        # Create products
                        products_data = city_data.get('products', [])
                        for product_data in products_data:
                            product_serializer = ProductSerializer(data={
                                **product_data,
                                'city': city.id
                            })
                            if product_serializer.is_valid():
                                product_serializer.save()
                            else:
                                errors.append({
                                    'city': city.name,
                                    'product': product_data.get('name', 'Unknown'),
                                    'errors': product_serializer.errors
                                })
                        
                        created_cities.append(city.name)
                    else:
                        errors.append({
                            'city': city_data.get('name', 'Unknown'),
                            'errors': city_serializer.errors
                        })
                
                except Exception as e:
                    errors.append({
                        'city': city_data.get('name', 'Unknown'),
                        'error': str(e)
                    })
            
            response_data = {
                'created_cities': created_cities,
                'count': len(created_cities)
            }
            
            if errors:
                response_data['errors'] = errors
                return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

class TechSpecViewSet(viewsets.ModelViewSet):
    queryset = TechSpec.objects.all()
    serializer_class = TechSpecSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_bulk_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return super().create(request, *args, **kwargs)
    
    def perform_bulk_create(self, serializer):
        return TechSpec.objects.bulk_create(
            [TechSpec(**item) for item in serializer.validated_data]
        )

# New viewsets for geographical data
class DivisionViewSet(viewsets.ModelViewSet):
    queryset = Division.objects.all()
    serializer_class = DivisionSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_bulk_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return super().create(request, *args, **kwargs)
    
    def perform_bulk_create(self, serializer):
        return Division.objects.bulk_create(
            [Division(**item) for item in serializer.validated_data]
        )
    
    @action(detail=False, methods=['post'])
    def bulk_import(self, request):
        """
        Bulk import Bangladesh geographical data
        """
        data = request.data
        
        if not isinstance(data, list):
            return Response(
                {"error": "Data should be a list of geographical entries"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_divisions = 0
        created_districts = 0
        created_thanas = 0
        errors = []
        
        for entry in data:
            try:
                # Create or get division
                division, created = Division.objects.get_or_create(
                    name=entry['division']
                )
                if created:
                    created_divisions += 1
                
                # Create or get district
                district, created = District.objects.get_or_create(
                    name=entry['district'],
                    division=division
                )
                if created:
                    created_districts += 1
                
                # Create thanas
                for thana_name in entry['thanas']:
                    thana, created = Thana.objects.get_or_create(
                        name=thana_name,
                        district=district
                    )
                    if created:
                        created_thanas += 1
                        
            except Exception as e:
                errors.append({
                    'entry': entry.get('_id', 'Unknown'),
                    'error': str(e)
                })
        
        response_data = {
            'created_divisions': created_divisions,
            'created_districts': created_districts,
            'created_thanas': created_thanas,
            'total_entries_processed': len(data)
        }
        
        if errors:
            response_data['errors'] = errors
            return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
        
        return Response(response_data, status=status.HTTP_201_CREATED)

class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = District.objects.all()
        division_id = self.request.query_params.get('division_id', None)
        if division_id is not None:
            queryset = queryset.filter(division_id=division_id)
        return queryset

class ThanaViewSet(viewsets.ModelViewSet):
    queryset = Thana.objects.all()
    serializer_class = ThanaSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = Thana.objects.all()
        district_id = self.request.query_params.get('district_id', None)
        if district_id is not None:
            queryset = queryset.filter(district_id=district_id)
        return queryset

@api_view(['GET'])
def bangladesh_data(request):
    """
    Get all Bangladesh geographical data
    """
    divisions = Division.objects.all()
    result = []
    
    for division in divisions:
        for district in division.districts.all():
            thanas = [thana.name for thana in district.thanas.all()]
            result.append({
                'division': division.name,
                'district': district.name,
                'thanas': thanas
            })
    
    return Response(result)

class ProductFeatureViewSet(viewsets.ModelViewSet):
    queryset = ProductFeature.objects.all()
    serializer_class = ProductFeatureSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def active_features(self, request):
        """
        Get only active product features
        """
        active_features = ProductFeature.objects.all()
        serializer = self.get_serializer(active_features, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        Handle both single and bulk creation
        """
        if isinstance(request.data, list):
            # Bulk creation
            return self.bulk_create(request, *args, **kwargs)
        else:
            # Single creation
            return super().create(request, *args, **kwargs)
    
    def bulk_create(self, request, *args, **kwargs):
        """
        Handle bulk creation of product features
        """
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_bulk_create(self, serializer):
        """
        Perform the bulk creation
        """
        ProductFeature.objects.bulk_create([
            ProductFeature(**item) for item in serializer.validated_data
        ])

def generate_qr_code(self):
    """Generate a QR code for the user's support link"""
    if not self.support_link:
        self.generate_support_link()
    
    try:
        # Create a QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.support_link)
        qr.make(fit=True)
        
        # Create an image from the QR code
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save the image to a buffer
        buffer = BytesIO()
        
        # Fix: Use the correct save method without the format parameter
        # Different versions of qrcode library handle this differently
        try:
            # Try with format parameter first (newer versions)
            img.save(buffer, format="PNG")
        except TypeError:
            # Fall back to without format parameter (older versions)
            img.save(buffer)
        
        # Convert to base64
        img_str = base64.b64encode(buffer.getvalue()).decode()
        self.qr_code = img_str
        self.save()
        return img_str
    except Exception as e:
        print(f"Error generating QR code: {str(e)}")
        import traceback
        traceback.print_exc()
        return ""

# Authentication and User Registration Views
@api_view(['POST'])
@permission_classes([AllowAny])
def send_verification_email(request):
    """Send verification email to user"""
    try:
        data = request.data
        email = data.get('email', '')
        
        if not email:
            return Response({
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            try:
                profile = user.profile
            except UserProfile.DoesNotExist:
                # Create profile if it doesn't exist
                profile = UserProfile.objects.create(user=user, role='customer')
            
            # Generate new verification token
            verification_token = str(uuid.uuid4())
            profile.verification_token = verification_token
            profile.is_email_verified = False
            profile.save()
            
            # Send verification email
            _send_verification_email_helper(user, verification_token)
            
            return Response({
                'message': 'Verification email sent successfully'
            })
        
        except User.DoesNotExist:
            return Response({
                'error': 'User with this email does not exist'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    """Verify email with token"""
    try:
        data = request.data
        email = data.get('email', '')
        token = data.get('token', '')
        
        if not email or not token:
            return Response({
                'error': 'Email and verification token are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            try:
                profile = user.profile
            except UserProfile.DoesNotExist:
                return Response({
                    'error': 'User profile not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            if profile.verification_token != token:
                return Response({
                    'error': 'Invalid verification token'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Mark email as verified
            profile.is_email_verified = True
            profile.verification_token = None
            
            # Generate QR code if it doesn't exist
            if not profile.qr_code:
                try:
                    qr_code = generate_service_qr_code(user.id)
                    profile.qr_code = qr_code
                    print(f"QR code generated and saved for user {user.id} after email verification")
                except Exception as qr_error:
                    print(f"QR code generation failed: {str(qr_error)}")
                    import traceback
                    traceback.print_exc()
            
            profile.save()
            
            # Generate token for Django API access
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'message': 'Email verified successfully',
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': profile.phone,
                    'role': profile.role
                },
                'qr_code': profile.qr_code
            })
        
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    #  """
    # The function `get_current_user` retrieves information about the current authenticated user using
    # Firebase or Django token authentication.
    
    # :param request: The code snippet you provided is a Django REST framework view function that
    # retrieves information about the current authenticated user. It first attempts to authenticate the
    # user using a Firebase token, and if that fails or Firebase is not available, it falls back to Django
    # token authentication
    # :return: The code snippet is a Django REST framework view function that retrieves information about
    # the current authenticated user. It first attempts to authenticate the user using a Firebase token,
    # and if that fails or Firebase is not available, it falls back to Django token authentication.
    # """ 
@api_view(['GET'])
@permission_classes([AllowAny])
def get_current_user(request):
    """Get current authenticated user information"""
    try:
        # Check for Firebase token in Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        user = None
        token = None

        # If no Bearer token is provided, allow session-authenticated users to be used
        if not auth_header.startswith('Bearer '):
            if request.user and request.user.is_authenticated:
                user = request.user
                print(f"get_current_user: using session-authenticated user: {user.username}")
            else:
                return Response({
                    'error': 'Authentication credentials were not provided.'
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            token = auth_header[7:]  # Remove 'Bearer ' prefix

            # If Firebase is not available, prefer session-based auth if present; otherwise 503
            from .firebase_config import is_firebase_available, verify_firebase_token
            if not is_firebase_available():
                if request.user and request.user.is_authenticated:
                    # Ignore the Bearer token and use the session-authenticated user
                    user = request.user
                else:
                    return Response({
                        'error': 'Firebase authentication is not available on the server.',
                        'message': 'Firebase is not configured or credentials are invalid.'
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            else:
                # Try to authenticate with Firebase token
                try:
                    decoded_token = verify_firebase_token(token)
                    print(f"get_current_user: decoded_token present: {bool(decoded_token)}")
                    if decoded_token:
                        firebase_uid = decoded_token.get('uid')
                        email = decoded_token.get('email')
                        print(f"get_current_user: decoded token keys: {list(decoded_token.keys())}")

                        # Try to find user by firebase_uid first
                        user = None
                        try:
                            if firebase_uid:
                                profile_obj = UserProfile.objects.filter(firebase_uid=firebase_uid).first()
                                if profile_obj:
                                    user = profile_obj.user
                        except Exception as e:
                            print(f"Error looking up UserProfile by firebase_uid: {e}")

                        # If not found by uid, try email
                        if not user:
                            try:
                                if email:
                                    user = User.objects.get(email=email)
                                    print(f"User found by email: {user.username}")
                                else:
                                    user = None
                            except User.DoesNotExist:
                                from .firebase_auth import get_or_create_user
                                user = get_or_create_user(firebase_uid, email, decoded_token.get('name'))
                                if not user:
                                    print(f"Failed to create or retrieve user for Firebase UID {firebase_uid} and email {email}")
                                    return Response({'error': 'Failed to create or retrieve user from Firebase token'}, status=status.HTTP_401_UNAUTHORIZED)

                except Exception as e:
                    print(f"Firebase authentication error: {str(e)}")
                    # Continue to try Django token authentication
        
        # If Firebase authentication failed or not available, try Django token authentication
        if not user:
            if not token:
                return Response({
                    'error': 'Authentication credentials were not provided.'
                }, status=status.HTTP_401_UNAUTHORIZED)
            try:
                token_obj = Token.objects.get(key=token)
                user = token_obj.user
            except Token.DoesNotExist:
                return Response({
                    'error': 'Invalid authentication token'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        # If we reach here, the user is authenticated
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            profile = UserProfile.objects.create(user=user, role='customer')
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined,
            'is_staff': user.is_staff,
            'profile': {
                'phone': profile.phone,
                'role': profile.role,
                'is_phone_verified': profile.is_phone_verified,
                'is_email_verified': profile.is_email_verified,
                'service_area_division': profile.service_area_division,
                'is_available': profile.is_available,
                'service_rating': float(profile.service_rating) if profile.service_rating else 0.0,
                'completed_jobs': profile.completed_jobs,
                'support_link': profile.support_link,
                'qr_code': profile.qr_code
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        # When DEBUG is enabled, include more details for troubleshooting
        debug_info = str(e) if getattr(settings, 'DEBUG', False) else 'An internal error occurred'
        return Response({
            'error': 'An error occurred while retrieving current user',
            'detail': debug_info
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_support_info(request):
    """Get support link and QR code for authenticated user"""
    try:
        # Check for Firebase token in Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        user = None
        token = None

        # Allow session-authenticated users when Bearer token is not provided
        if not auth_header.startswith('Bearer '):
            if request.user and request.user.is_authenticated:
                user = request.user
                print(f"get_support_info: using session-authenticated user: {user.username}")
            else:
                return Response({
                    'error': 'Authentication credentials were not provided.'
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            token = auth_header[7:]  # Remove 'Bearer ' prefix

            from .firebase_config import is_firebase_available
            if not is_firebase_available():
                if request.user and request.user.is_authenticated:
                    user = request.user
                else:
                    return Response({
                        'error': 'Firebase authentication is not available on the server.',
                        'message': 'Firebase is not configured or credentials are invalid.'
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            else:
                # Try to authenticate with Firebase token
                try:
                    from .firebase_auth import verify_firebase_token
                    decoded_token = verify_firebase_token(token)
                    if decoded_token:
                        firebase_uid = decoded_token.get('uid')
                        email = decoded_token.get('email')
                        
                        # Get user from Firebase UID or email
                        try:
                            user = User.objects.get(email=email)
                        except User.DoesNotExist:
                            return Response({
                                'error': 'User not found'
                            }, status=status.HTTP_404_NOT_FOUND)
                except Exception as e:
                    print(f"Firebase authentication error: {str(e)}")
                    # Continue to try Django token authentication
        
        # If Firebase authentication failed, try Django token authentication
        if not user:
            if not token:
                return Response({
                    'error': 'Authentication credentials were not provided.'
                }, status=status.HTTP_401_UNAUTHORIZED)
            try:
                token_obj = Token.objects.get(key=token)
                user = token_obj.user
            except Token.DoesNotExist:
                return Response({
                    'error': 'Invalid authentication token'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        # If we reach here, the user is authenticated
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            profile = UserProfile.objects.create(user=user, role='customer')
        
        # Ensure support link and QR code exist
        try:
            support_link = profile.support_link or profile.generate_support_link()
            qr_code = profile.qr_code or generate_service_qr_code(user.id)
        except Exception as e:
            # If QR code generation fails, continue without it
            print(f"QR code generation failed: {str(e)}")
            support_link = ""
            qr_code = ""
        
        return Response({
            'support_link': support_link,
            'qr_code': qr_code
        })
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
def generate_service_qr_code(user_id):
    """Generate a QR code for service requests"""
    try:
        # Create a unique service URL for this user
        service_url = f"http://localhost:3000/support/{user_id}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(service_url)
        qr.make(fit=True)
        
        # Convert to base64 string
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        
        # Fix: Use the correct save method without the format parameter
        try:
            # Try with format parameter first (newer versions)
            img.save(buffer, format="PNG")
        except TypeError:
            # Fall back to without format parameter (older versions)
            img.save(buffer)
            
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return img_str
    except Exception as e:
        print(f"Error generating QR code: {str(e)}")
        import traceback
        traceback.print_exc()
        return ""

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_all_users(request):
    """Get all users with their profile information including QR code and all important data"""
    try:
        users = User.objects.all().order_by('-date_joined')
        
        # Ensure all users have profiles and QR codes generated
        for user in users:
            try:
                profile = user.profile
            except UserProfile.DoesNotExist:
                # Create profile if it doesn't exist
                profile = UserProfile.objects.create(user=user, role='customer')
            
            # Generate support link if it doesn't exist
            if not profile.support_link:
                try:
                    profile.generate_support_link()
                except Exception as e:
                    print(f"Error generating support link for user {user.id}: {str(e)}")
            
            # Generate QR code if it doesn't exist (uses support_link)
            if not profile.qr_code:
                try:
                    profile.generate_qr_code()
                except Exception as e:
                    print(f"Error generating QR code for user {user.id}: {str(e)}")
        
        serializer = UserListSerializer(users, many=True)
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        })
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_users_firebase(request):
    """Get all users with Firebase authentication"""
    try:
        # If Firebase not available, return 503
        try:
            from .firebase_config import is_firebase_available
            if not is_firebase_available():
                return Response({
                    'error': 'Firebase authentication is not available on the server.',
                    'message': 'Firebase is not configured or credentials are invalid.'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception:
            pass

        # Check for Firebase token in Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith('Bearer '):
            return Response({
                'error': 'Authentication credentials were not provided.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Verify Firebase token
        try:
            from .firebase_auth import verify_firebase_token
            decoded_token = verify_firebase_token(token)
            if not decoded_token:
                return Response({
                    'error': 'Invalid authentication token'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Get user from Firebase UID or email
            firebase_uid = decoded_token.get('uid')
            email = decoded_token.get('email')
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if user is admin
            try:
                profile = user.profile
                # if profile.role != 'admin' and not user.is_staff:
                #     return Response({
                #         'error': 'Permission denied. Admin access required.'
                #     }, status=status.HTTP_403_FORBIDDEN)
            except UserProfile.DoesNotExist:
                return Response({
                    'error': 'User profile not found'
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({
                'error': f'Firebase authentication error: {str(e)}'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # If we reach here, the user is authenticated and is an admin
        users = User.objects.all().order_by('-date_joined')

        # Process users but avoid letting a single user's error cause a 500
        processed_users = []
        errors = []

        for user_item in users:
            try:
                try:
                    profile = user_item.profile
                except UserProfile.DoesNotExist:
                    profile = UserProfile.objects.create(user=user_item, role='customer')

                # Generate support link if missing (non-blocking)
                if not profile.support_link:
                    try:
                        profile.generate_support_link()
                    except Exception as e:
                        print(f"Error generating support link for user {user_item.id}: {str(e)}")
                        errors.append({'user_id': user_item.id, 'action': 'generate_support_link', 'error': str(e)})

                # Generate QR code if missing (non-blocking)
                if not profile.qr_code:
                    try:
                        profile.generate_qr_code()
                    except Exception as e:
                        print(f"Error generating QR code for user {user_item.id}: {str(e)}")
                        errors.append({'user_id': user_item.id, 'action': 'generate_qr_code', 'error': str(e)})

                processed_users.append(user_item)

            except Exception as e:
                # Log but continue processing remaining users
                import traceback
                traceback.print_exc()
                errors.append({'user_id': getattr(user_item, 'id', None), 'action': 'processing', 'error': str(e)})
                continue

        try:
            serializer = UserListSerializer(processed_users, many=True)
            response_data = {'count': len(serializer.data), 'results': serializer.data}
            if errors:
                response_data['errors'] = errors
                return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
            return Response(response_data)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': f'Failed to serialize users: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Phone Verification Views
@api_view(['POST'])
@permission_classes([AllowAny])
def send_phone_verification_code(request):
    """Send verification code to phone number"""
    try:
        data = request.data
        phone = data.get('phone', '')
        
        if not phone:
            return Response({
                'error': 'Phone number is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if phone number is registered
        is_registered, user = verify_phone_number(phone)
        
        if not is_registered:
            return Response({
                'error': 'Phone number is not registered. Please register first.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            profile = user.profile
            
            # Generate verification code
            verification_code = generate_verification_code()
            
            # Set expiration time (10 minutes from now)
            expires_at = datetime.now() + timedelta(minutes=10)
            
            # Save verification code and expiration time
            profile.verification_code = verification_code
            profile.verification_code_expires_at = expires_at
            profile.save()
            
            # Send SMS (this will also display in console)
            sms_sent = send_sms_verification(phone, verification_code)
            
            if sms_sent:
                return Response({
                    'message': 'Verification code sent successfully',
                    'code': verification_code,  # Include code in response for development
                    'expires_in': 600  # seconds
                })
            else:
                return Response({
                    'message': 'Verification code generated (check console)',
                    'code': verification_code,  # Include code even if SMS failed
                    'error': 'Failed to send SMS but code is available in console',
                    'expires_in': 600
                }, status=status.HTTP_202_ACCEPTED)  # Use 202 instead of 500 for partial success
                    
        except Exception as e:
            return Response({
                'error': f'An error occurred: {str(e)}',
                'code': verification_code if 'verification_code' in locals() else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_phone_code(request):
    """Verify phone number with code"""
    try:
        data = request.data
        phone = data.get('phone', '')
        code = data.get('code', '')
        
        if not phone or not code:
            return Response({
                'error': 'Phone number and verification code are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            profile = UserProfile.objects.get(phone=phone)
            
            # Check if verification code matches
            if profile.verification_code != code:
                return Response({
                    'error': 'Invalid verification code'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if verification code has expired
            if profile.verification_code_expires_at and profile.verification_code_expires_at < datetime.now():
                return Response({
                    'error': 'Verification code has expired'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Mark phone as verified
            profile.is_phone_verified = True
            profile.verification_code = None
            profile.verification_code_expires_at = None
            profile.save()
            
            # Generate token for Django API access
            token, created = Token.objects.get_or_create(user=profile.user)
            
            return Response({
                'message': 'Phone number verified successfully',
                'token': token.key,
                'user': {
                    'id': profile.user.id,
                    'username': profile.user.username,
                    'email': profile.user.email,
                    'first_name': profile.user.first_name,
                    'last_name': profile.user.last_name,
                    'phone': profile.phone,
                    'role': profile.role
                }
            })
            
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'Phone number not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def phone_login(request):
    """Login with phone number and verification code"""
    try:
        serializer = PhoneLoginSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            
            try:
                profile = UserProfile.objects.get(phone=phone)
                
                # If code is provided, verify it
                if 'code' in serializer.validated_data:
                    code = serializer.validated_data['code']
                    
                    # Check if verification code matches
                    if profile.verification_code != code:
                        return Response({
                            'error': 'Invalid verification code'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Check if verification code has expired
                    if profile.verification_code_expires_at and profile.verification_code_expires_at < datetime.now():
                        return Response({
                            'error': 'Verification code has expired'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Mark phone as verified
                    profile.is_phone_verified = True
                    profile.verification_code = None
                    profile.verification_code_expires_at = None
                    profile.save()
                
                # Generate token for Django API access
                token, created = Token.objects.get_or_create(user=profile.user)
                
                return Response({
                    'message': 'Login successful',
                    'token': token.key,
                    'user': {
                        'id': profile.user.id,
                        'username': profile.user.username,
                        'email': profile.user.email,
                        'first_name': profile.user.first_name,
                        'last_name': profile.user.last_name,
                        'phone': profile.phone,
                        'role': profile.role
                    }
                })
                
            except UserProfile.DoesNotExist:
                return Response({
                    'error': 'Phone number not found'
                }, status=status.HTTP_404_NOT_FOUND)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _send_verification_email_helper(user, token):
    """Helper function to send verification email to user"""
    try:
        subject = "Verify Your Email Address"
        verification_url = f"http://localhost:3000/verify-email?email={user.email}&token={token}"
        
        message = f"""
        Hi {user.first_name or user.username},
        
        Thank you for registering with our service. Please click the link below to verify your email address:
        
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you did not register for an account, please ignore this email.
        
        Thank you,
        The Team
        """
        
        # Get default from email or use a fallback
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@yourdomain.com')
        
        # Try to send the email
        result = send_mail(
            subject,
            message,
            from_email,
            [user.email],
            fail_silently=False  # Set to False to catch errors
        )
        
        print(f"Verification email sent to {user.email}. Result: {result}")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# Add a new view to manually resend verification email
@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_email(request):
    """Resend verification email to user"""
    try:
        data = request.data
        email = data.get('email', '')
        
        if not email:
            return Response({
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            try:
                profile = user.profile
            except UserProfile.DoesNotExist:
                # Create profile if it doesn't exist
                profile = UserProfile.objects.create(user=user, role='customer')
            
            # Generate new verification token
            verification_token = str(uuid.uuid4())
            profile.verification_token = verification_token
            profile.is_email_verified = False
            profile.save()
            
            # Send verification email
            email_sent = _send_verification_email_helper(user, verification_token)
            
            if email_sent:
                return Response({
                    'message': 'Verification email sent successfully'
                })
            else:
                return Response({
                    'message': 'Verification email generated but could not be sent. Please try again later.',
                    'token': verification_token  # Return token for development/testing
                }, status=status.HTTP_202_ACCEPTED)
        
        except User.DoesNotExist:
            return Response({
                'error': 'User with this email does not exist'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user and send email verification"""
    import traceback
    
    try:
        data = request.data
        print("Received data:", data)  # Debug log
        
        # Extract user data
        email = data.get('email', '').strip()
        username = data.get('username', '').strip() or email.split('@')[0] if email else ''
        password = data.get('password', str(uuid.uuid4())[:8])
        pin = data.get('pin', '')
        first_name = data.get('first_name', '').strip() or data.get('fullName', '').strip().split(' ')[0] if data.get('fullName') else ''
        last_name = data.get('last_name', '').strip() or ' '.join(data.get('fullName', '').strip().split(' ')[1:]) if data.get('fullName') and len(data.get('fullName', '').strip().split(' ')) > 1 else ''
        phone = data.get('phone', '').strip() or None  # Use None instead of empty string for unique field
        division = data.get('division', '').strip() or None
        district = data.get('district', '').strip() or None
        thana = data.get('thana', '').strip() or None
        address = data.get('address', '').strip() or data.get('addressDetails', '').strip() or None
        referral = data.get('referral', '').strip() or None
        notes = data.get('notes', '').strip() or None
        plan = data.get('plan', '').strip() or None
        role = data.get('role', 'customer')  # Default to customer role
        is_phone_verified = data.get('is_phone_verified', False)  # Get phone verification status
        
        # Validate required fields
        if not email:
            return Response({
                'error': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not pin:
            return Response({
                'error': 'PIN is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not username:
            username = email.split('@')[0] + str(uuid.uuid4().hex[:4])
        
        # Check if user with email already exists
        if User.objects.filter(email=email).exists():
            return Response({
                'error': 'User with this email already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if username already exists, generate unique one if needed
        original_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1
        
        # Check if phone already exists (if provided and not None)
        if phone and UserProfile.objects.filter(phone=phone).exists():
            return Response({
                'error': 'User with this phone number already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            print(f"User created successfully: {user.username}")
        except IntegrityError as e:
            return Response({
                'error': f'Failed to create user: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create the profile (signal might have created it)
        # Note: Signal creates profile automatically, so this should just get it
        try:
            profile = user.profile
            print(f"Profile already exists for user: {user.username}")
        except UserProfile.DoesNotExist:
            # This shouldn't happen due to signal, but handle it just in case
            profile = UserProfile.objects.create(user=user, role='customer')
            print(f"Profile created for user: {user.username}")
        
        # Update profile with provided data
        if phone:
            profile.phone = phone
        if pin:
            profile.pin = pin
        if role:
            profile.role = role
        if not profile.role:
            profile.role = 'customer'
        
        # Set phone verification status
        profile.is_phone_verified = is_phone_verified
        
        # Handle location data
        if division:
            try:
                division_obj = Division.objects.get(id=division)
                profile.service_area_division = division_obj.name
            except Division.DoesNotExist:
                pass
        
        if district:
            try:
                district_obj = District.objects.get(id=district)
                profile.service_area_district = district_obj.name
            except District.DoesNotExist:
                pass
        
        if thana:
            try:
                thana_obj = Thana.objects.get(id=thana)
                profile.service_area_thana = thana_obj.name
            except Thana.DoesNotExist:
                pass
        
        if address:
            profile.address = address
        if referral:
            profile.referral = referral
        if notes:
            profile.notes = notes
        
        # Generate verification token
        verification_token = str(uuid.uuid4())
        profile.verification_token = verification_token
        profile.is_email_verified = False
        
        # Generate support link if it doesn't exist
        if not profile.support_link:
            profile.generate_support_link()
        
        # Save profile first before generating QR code
        profile.save()
        print(f"Profile saved for user: {user.username}")
        
        # Generate QR code for service
        qr_code = ""
        try:
            profile.generate_qr_code()
            profile.save()  # Save again with QR code
            print(f"QR code generated and saved for user {user.id}")
        except Exception as qr_error:
            print(f"QR code generation failed: {str(qr_error)}")
            import traceback
            traceback.print_exc()
            # Continue without QR code for now
        
        # Send verification email (don't fail if email sending fails)
        try:
            email_sent = _send_verification_email_helper(user, verification_token)
            if not email_sent:
                print("Warning: Email sending failed, but continuing with registration")
        except Exception as email_error:
            print(f"Email sending failed: {str(email_error)}")
            # Continue anyway - email can be sent later
        
        # Generate token for Django API access
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'User registered successfully. Please check your email for verification.',
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'qr_code': profile.qr_code,  # Use profile.qr_code to ensure we get the latest
            'support_link': profile.support_link,  # Include support link
            'qr_code_generated': bool(profile.qr_code),  # Flag to indicate QR code is ready
            'verification_required': True,
            'phone_verified': is_phone_verified,  # Include phone verification status
            # Add token for automatic login
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': profile.phone,
                'role': profile.role,
                'qr_code': profile.qr_code,
                'support_link': profile.support_link,
                'is_phone_verified': profile.is_phone_verified
            }
        }, status=status.HTTP_201_CREATED)
    
    except IntegrityError as e:
        error_msg = str(e)
        if 'email' in error_msg.lower():
            return Response({
                'error': 'A user with this email already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        elif 'username' in error_msg.lower():
            return Response({
                'error': 'A user with this username already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        elif 'phone' in error_msg.lower():
            return Response({
                'error': 'A user with this phone number already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': f'Database error: {error_msg}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Registration error: {str(e)}")
        print(error_trace)
        return Response({
            'error': f'An error occurred: {str(e)}',
            'details': error_trace if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Firebase Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def firebase_login(request):
    """Login or register with Firebase ID token"""
    try:
        # Import here to avoid import errors if Firebase is not installed
        from .firebase_auth import firebase_initialized
        
        # Check if Firebase is initialized
        if not firebase_initialized:
            return Response({
                'error': 'Firebase authentication is not configured. Please contact the administrator.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        serializer = FirebaseTokenSerializer(data=request.data)
        if serializer.is_valid():
            id_token = serializer.validated_data['id_token']
            
            # Import here to avoid import errors if Firebase is not installed
            from .firebase_auth import verify_firebase_token, get_or_create_user
            
            # Verify the Firebase token
            decoded_token = verify_firebase_token(id_token)
            if not decoded_token:
                return Response({
                    'error': 'Invalid authentication token'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Get user info from token
            firebase_uid = decoded_token.get('uid')
            email = decoded_token.get('email')
            display_name = decoded_token.get('name')
            photo_url = decoded_token.get('picture')
            
            # Get or create user
            user = get_or_create_user(firebase_uid, email, display_name, photo_url)
            if not user:
                return Response({
                    'error': 'Failed to create user account'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get user profile
            try:
                profile = user.profile
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=user, role='customer')
            
            # Generate token for Django API access
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'message': 'Authentication successful',
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': profile.phone,
                    'role': profile.role,
                    'qr_code': profile.qr_code,
                    'is_phone_verified': profile.is_phone_verified,
                    'is_email_verified': profile.is_email_verified,
                }
            })
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def firebase_register(request):
    """Complete registration with additional info after Firebase authentication"""
    try:
        # Import here to avoid import errors if Firebase is not installed
        from .firebase_auth import firebase_initialized
        
        # Check if Firebase is initialized
        if not firebase_initialized:
            return Response({
                'error': 'Firebase authentication is not configured. Please contact the administrator.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        serializer = FirebaseRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            id_token = serializer.validated_data['id_token']
            
            # Import here to avoid import errors if Firebase is not installed
            from .firebase_auth import verify_firebase_token, get_or_create_user
            
            # Verify the Firebase token
            decoded_token = verify_firebase_token(id_token)
            if not decoded_token:
                return Response({
                    'error': 'Invalid authentication token'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Get user info from token
            firebase_uid = decoded_token.get('uid')
            email = decoded_token.get('email')
            display_name = decoded_token.get('name')
            
            # Get or create user in Django/PostgreSQL
            user = get_or_create_user(firebase_uid, email, display_name)
            if not user:
                return Response({
                    'error': 'Failed to create user account'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get user profile
            try:
                profile = user.profile
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=user, role='customer')
            
            # Update profile with additional info
            if 'phone' in serializer.validated_data:
                profile.phone = serializer.validated_data['phone']
            if 'role' in serializer.validated_data:
                profile.role = serializer.validated_data['role']
            if 'division' in serializer.validated_data:
                # Get division name instead of ID
                try:
                    division = Division.objects.get(id=serializer.validated_data['division'])
                    profile.service_area_division = division.name
                except Division.DoesNotExist:
                    pass
            if 'district' in serializer.validated_data:
                # Get district name instead of ID
                try:
                    district = District.objects.get(id=serializer.validated_data['district'])
                    profile.service_area_district = district.name
                except District.DoesNotExist:
                    pass
            if 'thana' in serializer.validated_data:
                # Get thana name instead of ID
                try:
                    thana = Thana.objects.get(id=serializer.validated_data['thana'])
                    profile.service_area_thana = thana.name
                except Thana.DoesNotExist:
                    pass
            if 'address' in serializer.validated_data:
                profile.address = serializer.validated_data['address']
            if 'referral' in serializer.validated_data:
                profile.referral = serializer.validated_data['referral']
            if 'notes' in serializer.validated_data:
                profile.notes = serializer.validated_data['notes']
            
            # Set phone verification status
            if 'is_phone_verified' in serializer.validated_data:
                profile.is_phone_verified = serializer.validated_data['is_phone_verified']
            
            # Generate support link if it doesn't exist
            if not profile.support_link:
                profile.generate_support_link()
            
            # Generate QR code if it doesn't exist
            if not profile.qr_code:
                try:
                    profile.generate_qr_code()
                    print(f"QR code generated for Firebase user {user.id}")
                except Exception as qr_error:
                    print(f"QR code generation failed: {str(qr_error)}")
            
            # Save profile with all data
            profile.save()
            
            # Generate token for Django API access
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'message': 'Registration successful',
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': profile.phone,
                    'role': profile.role,
                    'qr_code': profile.qr_code,
                    'support_link': profile.support_link,
                    'is_phone_verified': profile.is_phone_verified,
                    'is_email_verified': profile.is_email_verified,
                }
            })
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        # Log the error for debugging
        import traceback
        print(f"Firebase registration error: {str(e)}")
        print(traceback.format_exc())
        
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def test_firebase(request):
    """Test endpoint to check Firebase initialization status"""
    from .firebase_auth import firebase_initialized
    
    return Response({
        'firebase_initialized': firebase_initialized,
        'message': 'Firebase is initialized' if firebase_initialized else 'Firebase is not initialized. Check credentials configuration.',
        'status': 'ok' if firebase_initialized else 'not_configured'
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def regenerate_user_qr_code(request, user_id):
    """Regenerate QR code for a user - for admin use"""
    try:
        # Check for Firebase token in Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        user = None
        token = None
        
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            
            from .firebase_config import is_firebase_available
            if not is_firebase_available():
                if request.user and request.user.is_authenticated:
                    user = request.user
                else:
                    return Response({
                        'error': 'Firebase authentication is not available on the server.',
                        'message': 'Firebase is not configured or credentials are invalid.'
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            else:
                # Try to authenticate with Firebase token
                try:
                    from .firebase_auth import verify_firebase_token
                    decoded_token = verify_firebase_token(token)
                    if decoded_token:
                        firebase_uid = decoded_token.get('uid')
                        email = decoded_token.get('email')
                        
                        # Get user from Firebase UID or email
                        try:
                            user = User.objects.get(email=email)
                        except User.DoesNotExist:
                            return Response({
                                'error': 'User not found'
                            }, status=status.HTTP_404_NOT_FOUND)
                except Exception as e:
                    print(f"Firebase authentication error: {str(e)}")
                    # Continue to try Django token authentication
        
        # If Firebase authentication failed, try Django token authentication
        if not user:
            if not token:
                return Response({
                    'error': 'Authentication credentials were not provided.'
                }, status=status.HTTP_401_UNAUTHORIZED)
            try:
                token_obj = Token.objects.get(key=token)
                user = token_obj.user
            except Token.DoesNotExist:
                return Response({
                    'error': 'Invalid authentication token'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if user is admin
        try:
            profile = user.profile
            # if profile.role != 'admin' and not user.is_staff:
            #     return Response({
            #         'error': 'Permission denied. Admin access required.'
            #     }, status=status.HTTP_403_FORBIDDEN)
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'User profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            target_user = User.objects.get(id=user_id)
            target_profile = target_user.profile
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            target_profile = UserProfile.objects.create(user=target_user, role='customer')
        
        # Generate new support link
        target_profile.generate_support_link()
        
        # Generate new QR code
        target_profile.generate_qr_code()
        
        return Response({
            'message': 'QR code regenerated successfully',
            'qr_code': target_profile.qr_code,
            'support_link': target_profile.support_link
        })
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Update user profile
@api_view(['PUT'])
@permission_classes([AllowAny])
def update_user_profile(request, user_id):
    """Update user profile information - for admin use"""
    try:
        # Check for Firebase token in Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        user = None
        token = None
        
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            
            from .firebase_config import is_firebase_available
            if not is_firebase_available():
                if request.user and request.user.is_authenticated:
                    user = request.user
                else:
                    return Response({
                        'error': 'Firebase authentication is not available on the server.',
                        'message': 'Firebase is not configured or credentials are invalid.'
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            else:
                # Try to authenticate with Firebase token
                try:
                    from .firebase_auth import verify_firebase_token
                    decoded_token = verify_firebase_token(token)
                    if decoded_token:
                        firebase_uid = decoded_token.get('uid')
                        email = decoded_token.get('email')
                        
                        # Get user from Firebase UID or email
                        try:
                            user = User.objects.get(email=email)
                        except User.DoesNotExist:
                            return Response({
                                'error': 'User not found'
                            }, status=status.HTTP_404_NOT_FOUND)
                except Exception as e:
                    print(f"Firebase authentication error: {str(e)}")
                    # Continue to try Django token authentication
        
        # If Firebase authentication failed, try Django token authentication
        if not user:
            if not token:
                return Response({
                    'error': 'Authentication credentials were not provided.'
                }, status=status.HTTP_401_UNAUTHORIZED)
            try:
                token_obj = Token.objects.get(key=token)
                user = token_obj.user
            except Token.DoesNotExist:
                return Response({
                    'error': 'Invalid authentication token'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if user is admin
        try:
            profile = user.profile
            # if profile.role != 'admin' and not user.is_staff:
            #     return Response({
            #         'error': 'Permission denied. Admin access required.'
            #     }, status=status.HTTP_403_FORBIDDEN)
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'User profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            target_user = User.objects.get(id=user_id)
            target_profile = target_user.profile
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            target_profile = UserProfile.objects.create(user=target_user, role='customer')
        
        # Update user fields
        if 'first_name' in request.data:
            target_user.first_name = request.data['first_name']
        if 'last_name' in request.data:
            target_user.last_name = request.data['last_name']
        if 'email' in request.data:
            # Check if email is already used by another user
            new_email = request.data['email']
            if new_email != target_user.email and User.objects.filter(email=new_email).exists():
                return Response({
                    'error': 'Email is already in use by another user'
                }, status=status.HTTP_400_BAD_REQUEST)
            target_user.email = new_email
        
        target_user.save()
        
        # Update profile fields
        if 'phone' in request.data:
            # Check if phone is already used by another user
            new_phone = request.data['phone']
            if new_phone != target_profile.phone and UserProfile.objects.filter(phone=new_phone).exists():
                return Response({
                    'error': 'Phone number is already in use by another user'
                }, status=status.HTTP_400_BAD_REQUEST)
            target_profile.phone = new_phone
        
        if 'role' in request.data:
            target_profile.role = request.data['role']
        if 'service_area_division' in request.data:
            target_profile.service_area_division = request.data['service_area_division']
        if 'service_area_district' in request.data:
            target_profile.service_area_district = request.data['service_area_district']
        if 'service_area_thana' in request.data:
            target_profile.service_area_thana = request.data['service_area_thana']
        if 'address' in request.data:
            target_profile.address = request.data['address']
        if 'is_available' in request.data:
            target_profile.is_available = request.data['is_available']
        if 'service_rating' in request.data:
            target_profile.service_rating = request.data['service_rating']
        if 'completed_jobs' in request.data:
            target_profile.completed_jobs = request.data['completed_jobs']
        
        target_profile.save()
        
        return Response({
            'message': 'User profile updated successfully',
            'user': {
                'id': target_user.id,
                'username': target_user.username,
                'email': target_user.email,
                'first_name': target_user.first_name,
                'last_name': target_user.last_name,
                'profile': {
                    'phone': target_profile.phone,
                    'role': target_profile.role,
                    'service_area_division': target_profile.service_area_division,
                    'service_area_district': target_profile.service_area_district,
                    'service_area_thana': target_profile.service_area_thana,
                    'address': target_profile.address,
                    'is_available': target_profile.is_available,
                    'service_rating': float(target_profile.service_rating) if target_profile.service_rating else 0.0,
                    'completed_jobs': target_profile.completed_jobs,
                    'support_link': target_profile.support_link,
                    'qr_code': target_profile.qr_code,
                    'is_phone_verified': target_profile.is_phone_verified,
                    'is_email_verified': target_profile.is_email_verified,
                }
            }
        })
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def work_assignments(request):
    """List all work assignments or create a new one"""
    if request.method == 'GET':
        assignments = WorkAssignment.objects.all().order_by('-created_at')
        serializer = WorkAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = WorkAssignmentCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Set the assigned_by to current user
            assignment = serializer.save(assigned_by=request.user)
            
            # Create history entry
            AssignmentHistory.objects.create(
                assignment=assignment,
                changed_by=request.user,
                old_status='',
                new_status='pending',
                notes='Assignment created'
            )
            
            # Update technician availability if assigned
            if assignment.assigned_to:
                assignment.assigned_to.is_available = False
                assignment.assigned_to.save()
            
            return Response(WorkAssignmentSerializer(assignment).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def work_assignment_detail(request, pk):
    """Get, update or delete a specific work assignment"""
    try:
        assignment = WorkAssignment.objects.get(pk=pk)
    except WorkAssignment.DoesNotExist:
        return Response({'error': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = WorkAssignmentSerializer(assignment)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        old_status = assignment.status
        serializer = WorkAssignmentCreateSerializer(assignment, data=request.data, partial=True)
        if serializer.is_valid():
            updated_assignment = serializer.save()
            
            # Create history entry if status changed
            if 'status' in request.data and old_status != updated_assignment.status:
                AssignmentHistory.objects.create(
                    assignment=updated_assignment,
                    changed_by=request.user,
                    old_status=old_status,
                    new_status=updated_assignment.status,
                    notes=request.data.get('status_notes', '')
                )
                
                # Update completed_at if marked as completed
                if updated_assignment.status == 'completed' not in old_status:
                    from datetime import datetime
                    updated_assignment.completed_at = datetime.now()
                    
                    # Update technician availability
                    if updated_assignment.assigned_to:
                        updated_assignment.assigned_to.is_available = True
                        updated_assignment.assigned_to.save()
                
                updated_assignment.save()
            
            return Response(WorkAssignmentSerializer(updated_assignment).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        assignment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def technicians_list(request):
    """Get list of all technicians (service providers)"""
    technicians = UserProfile.objects.filter(role='provider').order_by('-service_rating')
    serializer = TechnicianListSerializer(technicians, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def settings_service_requests(request):
    """Admin endpoint: return all service requests for the dashboard

    Frontend expects `/api/settings/service-requests/`. This view enforces admin
    access and returns serialized service requests.
    """
    # Ensure authenticated
    if not (request.user and request.user.is_authenticated):
        return Response({'error': 'Authentication credentials were not provided.'}, status=status.HTTP_401_UNAUTHORIZED)

    # Only admin users should access settings service requests
    user_role = getattr(getattr(request.user, 'profile', None), 'role', None)
    if not (user_role == 'admin' or request.user.is_staff):
        return Response({'error': 'Permission denied. Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

    requests = ServiceRequest.objects.all().order_by('-created_at')
    serializer = ServiceRequestSerializer(requests, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def work_categories(request):
    """Get all work categories"""
    categories = WorkCategory.objects.all()
    serializer = WorkCategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_work_category(request):
    """Create a new work category"""
    serializer = WorkCategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assignment_statistics(request):
    """Get assignment statistics for dashboard"""
    from django.db.models import Count
    
    stats = {
        'total_assignments': WorkAssignment.objects.count(),
        'pending_assignments': WorkAssignment.objects.filter(status='pending').count(),
        'assigned_assignments': WorkAssignment.objects.filter(status='assigned').count(),
        'in_progress_assignments': WorkAssignment.objects.filter(status='in_progress').count(),
        'completed_assignments': WorkAssignment.objects.filter(status='completed').count(),
        'cancelled_assignments': WorkAssignment.objects.filter(status='cancelled').count(),
        'total_technicians': UserProfile.objects.filter(role='servicer').count(),
        'available_technicians': UserProfile.objects.filter(role='servicer', is_available=True).count(),
    }
    
    # Assignments by priority
    priority_stats = WorkAssignment.objects.values('priority').annotate(count=Count('id'))
    stats['by_priority'] = {item['priority']: item['count'] for item in priority_stats}
    
    # Recent assignments
    recent = WorkAssignment.objects.order_by('-created_at')[:5]
    stats['recent_assignments'] = WorkAssignmentSerializer(recent, many=True).data
    
    return Response(stats)

class ServiceRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ServiceRequest model with Firebase authentication support
    """
    # Support both Token and Firebase authentication
    authentication_classes = [FirebaseAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Only return service requests for the current user
        """
        return ServiceRequest.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions
        """
        if self.action == 'create':
            return ServiceRequestCreateSerializer
        return ServiceRequestSerializer
    
    def perform_create(self, serializer):
        """
        Set the user to the current authenticated user
        """
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)', authentication_classes=[FirebaseAuthentication, TokenAuthentication])
    def user_service_requests(self, request, user_id=None):
        """
        Get service requests for a specific user
        """
        # If client sent a Bearer token but Firebase is not available, return 503 (unless a session exists)
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            from .firebase_config import is_firebase_available
            if not is_firebase_available():
                if not (request.user and request.user.is_authenticated):
                    return Response({
                        'error': 'Firebase authentication is not available on the server.',
                        'message': 'Firebase is not configured or credentials are invalid.'
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Only allow users to see their own requests or if they are admin
        if not (request.user and request.user.is_authenticated):
            return Response({"error": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        if str(request.user.id) != user_id and not getattr(request.user.profile, 'role', None) == 'admin':
            return Response(
                {"error": "You don't have permission to view these requests"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        requests = ServiceRequest.objects.filter(user_id=user_id)
        serializer = self.get_serializer(requests, many=True) 
        return Response(serializer.data) 
    
@api_view(['GET'])
@permission_classes([AllowAny])
def firebase_status(request):
    """Check Firebase initialization status and return non-sensitive diagnostic info"""
    from .firebase_config import is_firebase_available, validate_firebase_credentials

    firebase_available = is_firebase_available()
    # Provide diagnostic reason without exposing secrets
    creds = getattr(settings, 'FIREBASE_CREDENTIALS', None)
    valid, reason = (False, 'No credentials configured')
    if creds:
        valid, reason = validate_firebase_credentials(creds)

    # Compose human-readable message and status for backward compatibility
    if firebase_available:
        message = 'Firebase is available on the server.'
        status_text = 'ok'
    else:
        if not creds:
            message = 'Firebase is not available on the server: No credentials configured.'
            status_text = 'not_configured'
        elif not valid:
            message = f"Firebase is not available on the server: {reason}."
            status_text = 'invalid_credentials'
        else:
            message = 'Firebase credentials appear valid but initialization failed. Check service account or permissions.'
            status_text = 'init_failed'

    return Response({
        'firebase_available': firebase_available,
        'credential_valid': valid,
        'diagnostic': reason if not valid else 'Credentials appear valid (initialization may still fail if service account revoked)',
        'message': message,
        'status': status_text,
        # Backwards-compatible 'error' field for older clients
        'error': reason if not valid else None,
    })