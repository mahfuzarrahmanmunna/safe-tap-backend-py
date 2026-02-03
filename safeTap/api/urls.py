from django.urls import path, include
from django.shortcuts import redirect
from rest_framework.routers import DefaultRouter
from .views import (
    CityPageDataViewSet,
    CityStatsViewSet,
    CityViewSet,
    ComparisonPointViewSet,
    FAQCategoryViewSet,
    FAQViewSet,
    HowItWorksStepViewSet,
    PricingPlanViewSet,
    ProductInfoViewSet,
    ReviewViewSet,
    SmartFeatureViewSet,
    TechSpecViewSet,
    DivisionViewSet,
    DistrictViewSet,
    TechSpecificationViewSet,
    TechStageViewSet,
    ThanaViewSet,
    ProductFeatureViewSet,
    WhyChoosePointViewSet,
    firebase_status,
    post_list,
    bangladesh_data,
    CustomAuthToken,
    register_user,
    send_verification_email,
    verify_email,
    get_current_user,
    get_support_info,
    get_all_users,
    get_all_users_firebase,
    api_root,
    send_phone_verification_code,
    verify_phone_code,
    phone_login,
    login_user,
    resend_verification_email,
    test_firebase,
    update_user_profile,
    regenerate_user_qr_code,
    work_assignments,
    work_assignment_detail,
    technicians_list,
    work_categories,
    create_work_category,
    assignment_statistics,
    firebase_login,
    firebase_register,
    ServiceRequestViewSet,
    CitySlideViewSet
)


def _normalize_api_prefix(request, subpath=''):
    """Normalize duplicated API prefixes: /api/api/... -> /api/..."""
    try:
        if subpath and subpath.startswith('api/'):
            rest = subpath[len('api/'):]
            target = '/api/' + rest
        else:
            # If someone requested /api/api (no trailing path) or similar
            target = '/api/' + (subpath or '')

        # Preserve querystring
        qs = request.META.get('QUERY_STRING', '')
        if qs:
            target = target + '?' + qs
        return redirect(target, permanent=False)
    except Exception:
        # Fallback: do a safe redirect to root API
        return redirect('/api/', permanent=False)

# Create a router and register your viewsets
router = DefaultRouter()
router.register(r'cities', CityViewSet)
router.register(r'tech-specs', TechSpecViewSet)
router.register(r'divisions', DivisionViewSet)
router.register(r'districts', DistrictViewSet)
router.register(r'thanas', ThanaViewSet)
router.register(r'product-features', ProductFeatureViewSet)
router.register(r'service-requests', ServiceRequestViewSet, basename='service-request')
router.register(r'city-slides', CitySlideViewSet)
router.register(r'city-stats', CityStatsViewSet)
router.register(r'tech-specifications', TechSpecificationViewSet)
router.register(r'smart-features', SmartFeatureViewSet)
router.register(r'tech-stages', TechStageViewSet)
router.register(r'faq-categories', FAQCategoryViewSet)
router.register(r'faqs', FAQViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'why-choose-points', WhyChoosePointViewSet)
router.register(r'how-it-works-steps', HowItWorksStepViewSet)
router.register(r'pricing-plans', PricingPlanViewSet)
router.register(r'product-info', ProductInfoViewSet)
router.register(r'comparison-points', ComparisonPointViewSet)


# Define the URL patterns
# IMPORTANT: Order matters! More specific paths must come before general ones.
urlpatterns = [
    # Normalize duplicated /api/ prefix (e.g., /api/api/divisions/ -> /api/divisions/)
    # Place this BEFORE other patterns so it runs early and avoids 404s from double prefixes.
    path('api/<path:subpath>/', _normalize_api_prefix),
    path('api/', _normalize_api_prefix),

    # The root path for your API (e.g., /api/)
    # This MUST come before 'include(router.urls)' to be reached.
    path('', api_root, name='api_root'),

    # Backwards-compatible routes used by frontend
    path('technicians/', technicians_list, name='technicians_list_public'),
    path('settings/service-requests/', lambda request: redirect('/api/auth/assignments/'), name='settings_service_requests_redirect'),

    # Authentication-related endpoints
    path('auth/token/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('auth/register/', register_user, name='register-user'),
    path('auth/login/', login_user, name='login_user'),
    path('auth/send-email/', send_verification_email, name='send_verification_email'),
    path('auth/verify-email/', verify_email, name='verify_email'),
    path('auth/me/', get_current_user, name='get_current_user'),  # Get current user info
    path('auth/support/', get_support_info, name='get_support_info'), # Support endpoint
    path('auth/users/', get_all_users, name='get_all_users'),  # Get all users with Django auth
    path('auth/users/firebase/', get_all_users_firebase, name='get_all_users_firebase'),  # Get all users with Firebase auth
    
    # Phone verification endpoints
    path('auth/phone/send-code/', send_phone_verification_code, name='send_phone_verification_code'),
    path('auth/phone/verify/', verify_phone_code, name='verify_phone_code'),
    path('auth/phone/login/', phone_login, name='phone_login'),
    
    # Other specific function-based views
    path('posts/', post_list, name='post-list'),
    path('bangladesh-data/', bangladesh_data, name='bangladesh-data'),
    path('auth/resend-verification-email/', resend_verification_email, name='resend_verification_email'),
    
    # Include all URLs from the router (for ViewSets)
    # This will handle URLs like /api/cities/, /api/divisions/, etc.
    path('', include(router.urls)),
    
    path('test-firebase/', test_firebase, name='test_firebase'),
    
    # You can add more specific paths here if needed
    path('auth/firebase/login/', firebase_login, name='firebase_login'),
    path('auth/firebase/register/', firebase_register, name='firebase_register'),

    # Admin endpoints
    path('admin/users/<int:user_id>/', update_user_profile, name='update_user_profile'),
    path('admin/users/<int:user_id>/regenerate-qr/', regenerate_user_qr_code, name='regenerate_user_qr_code'),

    # Work assignment endpoints
    path('auth/assignments/', work_assignments, name='work_assignments'),
    path('auth/assignments/<int:pk>/', work_assignment_detail, name='work_assignment_detail'),
    path('auth/technicians/', technicians_list, name='technicians_list'),
    path('auth/work-categories/', work_categories, name='work_categories'),
    path('auth/work-categories/create/', create_work_category, name='create_work_category'),
    path('auth/assignment-stats/', assignment_statistics, name='assignment_statistics'),
    
    
    # Firebase status endpoint (reachable at /api/auth/firebase/status/)
    path('auth/firebase/status/', firebase_status, name='firebase_status'),
    
    
     path('city-page-data/', CityPageDataViewSet.as_view({'get': 'list'}), name='city-page-data'),
]