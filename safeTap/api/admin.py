# Update your api/admin.py file
from django.contrib import admin
from .models import (
    Post, City, CitySlide, CityStats, Product, TechSpec, TechSpecification,
    Division, District, Thana, ProductFeature, UserProfile, ServiceRequest,
    ServiceRequestImage, ServiceRequestVideo, TechStage, SmartFeature,
    FAQCategory, FAQ, Review, WhyChoosePoint, HowItWorksStep, PricingPlan,
    ProductInfo, ComparisonPoint,
)

# Register your models here.

# @admin.register(CitySlide)
# class CitySlideAdmin(admin.ModelAdmin):
#     list_display = ('city', 'title')
#     list_filter = ('city',)

# @admin.register(CityStats)
# class CityStatsAdmin(admin.ModelAdmin):
#     list_display = ('city', 'users', 'rating', 'installations')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('city', 'name', 'price')
    list_filter = ('city',)

@admin.register(TechSpec)
class TechSpecAdmin(admin.ModelAdmin):
    list_display = ('icon_name', 'title', 'details')

@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'division')
    list_filter = ('division',)
    search_fields = ('name',)

@admin.register(Thana)
class ThanaAdmin(admin.ModelAdmin):
    list_display = ('name', 'district')
    list_filter = ('district',)
    search_fields = ('name',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'role', 'is_phone_verified', 'is_email_verified')
    list_filter = ('role', 'is_phone_verified', 'is_email_verified')
    search_fields = ('user__username', 'user__email', 'phone')
    readonly_fields = ('qr_code',)

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'technician', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email', 'problem_description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ServiceRequestImage)
class ServiceRequestImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'service_request', 'uploaded_at')
    readonly_fields = ('uploaded_at',)

@admin.register(ServiceRequestVideo)
class ServiceRequestVideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'service_request', 'uploaded_at')
    readonly_fields = ('uploaded_at',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('title', 'content')


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(CitySlide)
class CitySlideAdmin(admin.ModelAdmin):
    list_display = ('city', 'product_type', 'title', 'order', 'is_active')
    list_filter = ('city', 'product_type', 'is_active')
    search_fields = ('title', 'subtitle', 'city__name')
    list_editable = ('order', 'is_active')

@admin.register(CityStats)
class CityStatsAdmin(admin.ModelAdmin):
    list_display = ('city', 'users', 'rating', 'installations')
    search_fields = ('city__name',)

@admin.register(ProductFeature)
class ProductFeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    list_editable = ('order', 'is_active')

@admin.register(TechSpecification)
class TechSpecificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon_name', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'details')
    list_editable = ('order', 'is_active')

@admin.register(SmartFeature)
class SmartFeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    list_editable = ('order', 'is_active')

@admin.register(TechStage)
class TechStageAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)
    list_editable = ('order', 'is_active')

@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'is_active')
    list_editable = ('order', 'is_active')

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'order', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('question', 'answer')
    list_editable = ('order', 'is_active')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'city', 'is_verified', 'is_active', 'created_at')
    list_filter = ('rating', 'is_verified', 'is_active', 'created_at')
    search_fields = ('name', 'comment', 'city')
    list_editable = ('is_verified', 'is_active')

@admin.register(WhyChoosePoint)
class WhyChoosePointAdmin(admin.ModelAdmin):
    list_display = ('label', 'title', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('label', 'title', 'description')
    list_editable = ('order', 'is_active')

@admin.register(HowItWorksStep)
class HowItWorksStepAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon_class', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)
    list_editable = ('order', 'is_active')

@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display = ('product_type', 'plan_name', 'price_28_days', 'price_90_days', 'price_360_days', 'is_active')
    list_filter = ('product_type', 'is_active')
    search_fields = ('product_type', 'plan_name')
    list_editable = ('is_active',)

@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ('product_type', 'name', 'is_active')
    list_filter = ('product_type', 'is_active')
    search_fields = ('product_type', 'name', 'subtitle')

@admin.register(ComparisonPoint)
class ComparisonPointAdmin(admin.ModelAdmin):
    list_display = ('category', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('category',)
    list_editable = ('order', 'is_active')