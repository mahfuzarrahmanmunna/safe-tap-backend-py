import uuid
import qrcode
from io import BytesIO
import base64
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.title


# Authentication related model
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('servicer', 'Service Provider/Technician'),
        ('admin', 'Super Admin'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    firebase_uid = models.CharField(max_length=128, blank=True, null=True, unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=255, blank=True, null=True)
    verification_code = models.CharField(max_length=10, blank=True, null=True)
    verification_code_expires_at = models.DateTimeField(blank=True, null=True)
    pin = models.CharField(max_length=10, blank=True, null=True)  # Add this field
    service_area_division = models.CharField(max_length=100, blank=True, null=True)
    service_area_district = models.CharField(max_length=100, blank=True, null=True)
    service_area_thana = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    is_available = models.BooleanField(default=False)
    service_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    completed_jobs = models.IntegerField(default=0)
    support_link = models.URLField(blank=True, null=True)
    qr_code = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
    def generate_support_link(self):
        """Generate a unique support link for this user"""
        if not self.support_link:
            self.support_link = f"http://localhost:3000/support/{self.user.id}"
            self.save()
        return self.support_link
    
    def generate_qr_code(self):
        """Generate QR code for this user's support link"""
        try:
            # Generate support link first if it doesn't exist
            if not self.support_link:
                self.generate_support_link()
            
            # Create the QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(self.support_link)
            qr.make(fit=True)
            
            # Create an image from the QR Code
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert the image to a base64 string
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            self.qr_code = img_str
            self.save()
            return img_str
        except Exception as e:
            print(f"Error generating QR code: {str(e)}")
            import traceback
            traceback.print_exc()
            return ""


# Add a signal to create UserProfile when a User is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Only create if it doesn't already exist (to avoid conflicts)
        profile, profile_created = UserProfile.objects.get_or_create(user=instance)
        
        # Generate support link and QR code for new user
        if profile_created:
            profile.generate_support_link()
            profile.generate_qr_code()
            print(f"Profile with QR code created for user: {instance.username}")


# Add this Customer model that was missing
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"


class WorkCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # Icon name
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Work Category"
        verbose_name_plural = "Work Categories"


class WorkAssignment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  # Fixed reference to Customer model
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(WorkCategory, on_delete=models.SET_NULL, null=True)
    assigned_to = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_assignments')
    client_name = models.CharField(max_length=200)
    client_phone = models.CharField(max_length=15, blank=True)
    client_email = models.EmailField(blank=True)
    client_address = models.TextField(blank=True)
    
    # Location details
    division = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    thana = models.CharField(max_length=100, blank=True)
    full_address = models.TextField(blank=True)
    
    # Schedule
    scheduled_date = models.DateTimeField(null=True, blank=True)
    estimated_duration = models.CharField(max_length=100, blank=True)  # e.g., "2 hours", "1 day"
    
    # Status and priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Pricing
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Additional notes
    admin_notes = models.TextField(blank=True)
    technician_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    class Meta:
        verbose_name = "Work Assignment"
        verbose_name_plural = "Work Assignments"
        ordering = ['-created_at']


class AssignmentHistory(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    assignment = models.ForeignKey(WorkAssignment, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"History for {self.assignment.title}"
    
    class Meta:
        verbose_name = "Assignment History"
        verbose_name_plural = "Assignment Histories"
        ordering = ['-timestamp']
        
        
class ServiceRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_requests')
    problem_description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    technician = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_requests',
        limit_choices_to={'profile__role': 'servicer'}
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Service Request #{self.id} - {self.user.username}"


class ServiceRequestImage(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='service_requests/images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for Request #{self.service_request.id}"


class ServiceRequestVideo(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='service_requests/videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Video for Request #{self.service_request.id}"


# New models for Bangladesh geographical data
class Division(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Division"
        verbose_name_plural = "Divisions"


class District(models.Model):
    name = models.CharField(max_length=100)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='districts')
    
    def __str__(self):
        return f"{self.name}, {self.division.name}"
    
    class Meta:
        unique_together = ('name', 'division')
        verbose_name = "District"
        verbose_name_plural = "Districts"


class Thana(models.Model):
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='thanas')
    
    def __str__(self):
        return f"{self.name}, {self.district.name}"
    
    class Meta:
        unique_together = ('name', 'district')
        verbose_name = "Thana"
        verbose_name_plural = "Thanas"


class City(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class CitySlide(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='slides')
    product_type = models.CharField(max_length=20, choices=[
        ('copper', 'Copper'),
        ('ro_plus', 'RO+'),
        ('alkaline', 'Alkaline'),
    ], default='copper')
    title = models.CharField(max_length=200, blank=True, default='')
    subtitle = models.CharField(max_length=200, blank=True, default='')
    description = models.TextField(blank=True, default='')
    image = models.ImageField(upload_to='city_slides/', blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True, default='')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.city.name} - {self.product_type} - {self.title}"


class CityStats(models.Model):
    city = models.OneToOneField(City, on_delete=models.CASCADE, related_name='stats')
    users = models.CharField(max_length=50)
    rating = models.CharField(max_length=10)
    installations = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.city.name} Stats"


class Product(models.Model):
    city = models.ForeignKey('City', related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price = models.CharField(max_length=50)
    features = models.JSONField(blank=True, default=list)  # Using JSONField for features array
    description = models.TextField()
    
    def __str__(self):
        return f"{self.city.name} - {self.name}"


class ProductFeature(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='product_features/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title


class TechSpec(models.Model):
    icon_name = models.CharField(max_length=50)  # Store icon name like "Shield", "Zap"
    title = models.CharField(max_length=200)
    details = models.CharField(max_length=200)
    
    def __str__(self):
        return self.title


class TechSpecification(models.Model):
    icon_name = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    details = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title


class SmartFeature(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='smart_features/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title


class TechStage(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='tech_stages/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title


class FAQCategory(models.Model):
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        verbose_name_plural = "FAQ Categories"
    
    def __str__(self):
        return self.name


class FAQ(models.Model):
    category = models.ForeignKey(FAQCategory, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=500)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.question


class Review(models.Model):
    name = models.CharField(max_length=100)
    rating = models.PositiveIntegerField(default=5)  # 1-5
    comment = models.TextField()
    avatar = models.ImageField(upload_to='review_avatars/', blank=True, null=True)
    city = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.rating}/5"


class WhyChoosePoint(models.Model):
    label = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='why_choose_points/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title


class HowItWorksStep(models.Model):
    title = models.CharField(max_length=200)
    icon_class = models.CharField(max_length=100)  # Font Awesome class name
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title


class PricingPlan(models.Model):
    product_type = models.CharField(max_length=20, choices=[
        ('copper', 'Copper'),
        ('ro_plus', 'RO+'),
        ('alkaline', 'Alkaline'),
    ])
    plan_name = models.CharField(max_length=100)  # e.g., "Couple", "Family", "Unlimited"
    plan_details = models.CharField(max_length=100)  # e.g., "200 ltrs/m"
    price_28_days = models.DecimalField(max_digits=10, decimal_places=2)
    price_90_days = models.DecimalField(max_digits=10, decimal_places=2)
    price_360_days = models.DecimalField(max_digits=10, decimal_places=2)
    savings = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['product_type', 'plan_name']
    
    def __str__(self):
        return f"{self.product_type} - {self.plan_name}"


class ProductInfo(models.Model):
    product_type = models.CharField(max_length=20, choices=[
        ('copper', 'Copper'),
        ('ro_plus', 'RO+'),
        ('alkaline', 'Alkaline'),
    ])
    name = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['product_type']
    
    def __str__(self):
        return f"{self.product_type} - {self.name}"


class ComparisonPoint(models.Model):
    category = models.CharField(max_length=100)
    water_can_description = models.TextField()
    other_purifier_description = models.TextField()
    safetap_description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.category
    
