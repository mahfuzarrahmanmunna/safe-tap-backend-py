from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import (
    Post, City, CitySlide, CityStats, Product, TechSpec,
    Division, District, Thana, ProductFeature, UserProfile,
    WorkCategory, WorkAssignment, AssignmentHistory
)

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
    readonly_fields = ('support_link', 'qr_code_preview')
    
    def qr_code_preview(self, obj):
        if obj.qr_code:
            return mark_safe(f'<img src="data:image/png;base64,{obj.qr_code}" width="100" height="100" />')
        return "No QR Code"
    qr_code_preview.short_description = 'QR Code'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'phone', 'role', 'is_phone_verified', 'is_email_verified')
        }),
        ('Service Area', {
            'fields': ('service_area_division', 'service_area_district', 'service_area_thana', 'address')
        }),
        ('Service Provider', {
            'fields': ('is_available', 'service_rating', 'completed_jobs')
        }),
        ('Support Information', {
            'fields': ('support_link', 'qr_code_preview'),
            'classes': ('collapse',)
        }),
        ('Additional', {
            'fields': ('referral', 'notes', 'firebase_uid'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Auto-assign admin role to staff users"""
        if request.user.is_staff and not change:
            # Optionally auto-set role for new users created from admin
            pass
        super().save_model(request, obj, form, change)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('title', 'content')

@admin.register(WorkCategory)
class WorkCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(WorkAssignment)
class WorkAssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'customer', 'assigned_to', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'category', 'created_at')
    search_fields = ('title', 'description', 'customer__username')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'category', 'customer', 'assigned_to', 'assigned_by')
        }),
        ('Status', {
            'fields': ('status', 'priority')
        }),
        ('Location', {
            'fields': ('division', 'district', 'thana', 'address')
        }),
        ('Timing', {
            'fields': ('scheduled_date', 'completed_at')
        }),
        ('Pricing', {
            'fields': ('estimated_cost', 'actual_cost')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(AssignmentHistory)
class AssignmentHistoryAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'changed_by', 'old_status', 'new_status', 'created_at')
    list_filter = ('new_status', 'old_status', 'created_at')
    search_fields = ('assignment__title', 'changed_by__username')
    readonly_fields = ('created_at',)
