from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    City, CitySlide, CityStats, Product, TechSpec, Division, District, Thana,
    ProductFeature, UserProfile, Post, WorkAssignment, WorkCategory, AssignmentHistory, ServiceRequest,
    ServiceRequestImage, ServiceRequestVideo, TechSpecification,
    SmartFeature, TechStage, FAQCategory, FAQ, Review, WhyChoosePoint,
    HowItWorksStep, PricingPlan, ProductInfo, ComparisonPoint
)

class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = '__all__'

class DistrictSerializer(serializers.ModelSerializer):
    division_name = serializers.CharField(source='division.name', read_only=True)
    
    class Meta:
        model = District
        fields = '__all__'

class ThanaSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source='district.name', read_only=True)
    division_name = serializers.CharField(source='district.division.name', read_only=True)
    
    class Meta:
        model = Thana
        fields = '__all__'

class BangladeshDataSerializer(serializers.Serializer):
    division = serializers.CharField()
    district = serializers.CharField()
    thanas = serializers.ListField(child=serializers.CharField())

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

class CitySlideSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CitySlide
        fields = '__all__'
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class CityStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CityStats
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class CityDetailSerializer(serializers.ModelSerializer):
    slides = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()
    
    class Meta:
        model = City
        fields = ['id', 'name', 'slug', 'slides', 'stats']
    
    def get_slides(self, obj):
        slides = CitySlide.objects.filter(city=obj, is_active=True)
        result = {}
        for slide in slides:
            if slide.product_type not in result:
                result[slide.product_type] = []
            result[slide.product_type].append(CitySlideSerializer(slide, context=self.context).data)
        return result
    
    def get_stats(self, obj):
        try:
            stats = CityStats.objects.get(city=obj)
            return CityStatsSerializer(stats).data
        except CityStats.DoesNotExist:
            return None

class TechSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechSpec
        fields = '__all__'

class ProductFeatureSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductFeature
        fields = '__all__'
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class TechSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechSpecification
        fields = '__all__'

class SmartFeatureSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = SmartFeature
        fields = '__all__'
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class TechStageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = TechStage
        fields = '__all__'
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class FAQCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQCategory
        fields = '__all__'

class FAQSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = FAQ
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = '__all__'
    
    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None

class WhyChoosePointSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = WhyChoosePoint
        fields = '__all__'
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class HowItWorksStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = HowItWorksStep
        fields = '__all__'

class PricingPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingPlan
        fields = '__all__'

class ProductInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInfo
        fields = '__all__'

class ComparisonPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComparisonPoint
        fields = '__all__'

class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False, write_only=True)
    pin = serializers.CharField(required=True, min_length=4, max_length=6)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    fullName = serializers.CharField(required=False, write_only=True)
    phone = serializers.CharField(required=False)
    division = serializers.CharField(required=False)
    district = serializers.CharField(required=False)
    thana = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    addressDetails = serializers.CharField(required=False, write_only=True)
    referral = serializers.CharField(required=False)
    notes = serializers.CharField(required=False)
    plan = serializers.CharField(required=False)
    role = serializers.CharField(required=False)
    is_phone_verified = serializers.BooleanField(default=False)

class SupportLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['support_link', 'qr_code']

# The `UserListSerializer` class serializes user data along with their profile information in Django
# REST framework.
class UserListSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'is_staff', 'profile']
    
    def get_profile(self, obj):
        try:
            profile = obj.profile
            return {
                'phone': profile.phone,
                'role': profile.role,
                'is_phone_verified': profile.is_phone_verified,
                'is_email_verified': profile.is_email_verified,
                'service_area_division': profile.service_area_division,
                'service_area_district': profile.service_area_district,
                'service_area_thana': profile.service_area_thana,
                'address': profile.address,
                'is_available': profile.is_available,
                'service_rating': float(profile.service_rating) if profile.service_rating else 0.0,
                'completed_jobs': profile.completed_jobs,
                'support_link': profile.support_link,
                'qr_code': profile.qr_code,
            }
        except UserProfile.DoesNotExist:
            return None

class PhoneVerificationSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)

class CodeVerificationSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    code = serializers.CharField(required=True, min_length=4, max_length=6)

class PhoneLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    code = serializers.CharField(required=False, min_length=4, max_length=6)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    pin = serializers.CharField(required=True, min_length=4, max_length=6)
    bypass_email_verification = serializers.BooleanField(default=False)

class FirebaseTokenSerializer(serializers.Serializer):
    id_token = serializers.CharField(required=True)

class FirebaseRegistrationSerializer(serializers.Serializer):
    id_token = serializers.CharField(required=True)
    phone = serializers.CharField(required=False)
    role = serializers.CharField(required=False)
    division = serializers.CharField(required=False)
    district = serializers.CharField(required=False)
    thana = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    referral = serializers.CharField(required=False)
    notes = serializers.CharField(required=False)
    is_phone_verified = serializers.BooleanField(default=False)

class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['author']

class WorkCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkCategory
        fields = '__all__'

class TechnicianListSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user_name', 'user_email', 'phone', 'service_area_division',
            'service_area_district', 'service_area_thana', 'is_available',
            'service_rating', 'completed_jobs', 'support_link', 'qr_code'
        ]

class AssignmentHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source='changed_by.username', read_only=True)
    
    class Meta:
        model = AssignmentHistory
        fields = '__all__'

class WorkAssignmentSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    technician_name = serializers.CharField(source='assigned_to.user.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.username', read_only=True)
    history = AssignmentHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = WorkAssignment
        fields = '__all__'

class WorkAssignmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkAssignment
        exclude = ['assigned_by', 'completed_at']

class ServiceRequestImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceRequestImage
        fields = ['id', 'image', 'image_url', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class ServiceRequestVideoSerializer(serializers.ModelSerializer):
    video = serializers.FileField(required=True)
    video_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceRequestVideo
        fields = ['id', 'video', 'video_url', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']
    
    def get_video_url(self, obj):
        if obj.video:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.video.url)
            return obj.video.url
        return None

class TechnicianSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'name', 'phone']
    
    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username
    
    def get_phone(self, obj):
        return getattr(obj.profile, 'phone', None) if hasattr(obj, 'profile') else None

class ServiceRequestSerializer(serializers.ModelSerializer):
    images = ServiceRequestImageSerializer(many=True, read_only=True)
    videos = ServiceRequestVideoSerializer(many=True, read_only=True)
    technician = TechnicianSerializer(read_only=True)
    
    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'user', 'problem_description', 'status', 
            'created_at', 'updated_at', 'technician', 'notes',
            'images', 'videos'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'technician']

class ServiceRequestCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    videos = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = ServiceRequest
        fields = [
            'problem_description', 'status', 'notes', 'images', 'videos'
        ]
    
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        videos_data = validated_data.pop('videos', [])
        
        service_request = ServiceRequest.objects.create(**validated_data)
        
        # Create image objects
        for image in images_data:
            ServiceRequestImage.objects.create(
                service_request=service_request,
                image=image
            )
        
        # Create video objects
        for video in videos_data:
            ServiceRequestVideo.objects.create(
                service_request=service_request,
                video=video
            )
        
        return service_request