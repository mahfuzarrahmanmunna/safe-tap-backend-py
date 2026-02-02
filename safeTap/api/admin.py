# Update your api/admin.py file
from django.contrib import admin
from .models import (
    Post, City, CitySlide, CityStats, Product, TechSpec,
    Division, District, Thana, ProductFeature, UserProfile, ServiceRequest, ServiceRequestImage, ServiceRequestVideo
)

# Register your models here.

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)

@admin.register(CitySlide)
class CitySlideAdmin(admin.ModelAdmin):
    list_display = ('city', 'title')
    list_filter = ('city',)

@admin.register(CityStats)
class CityStatsAdmin(admin.ModelAdmin):
    list_display = ('city', 'users', 'rating', 'installations')

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

@admin.register(ProductFeature)
class ProductFeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title',)

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
