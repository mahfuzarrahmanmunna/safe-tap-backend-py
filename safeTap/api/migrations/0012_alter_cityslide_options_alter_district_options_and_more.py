from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_userprofile_address_and_more'),
    ]

    operations = [
        # Skip adding fields that already exist in the database
        # These fields were added manually: created_at, updated_at, referral, notes, nid
        
        # Keep other operations that don't conflict
        migrations.AlterModelOptions(
            name='cityslide',
            options={'ordering': ['order']},
        ),
        migrations.AlterModelOptions(
            name='district',
            options={},
        ),
        migrations.AlterModelOptions(
            name='division',
            options={},
        ),
        migrations.AlterModelOptions(
            name='productfeature',
            options={},
        ),
        migrations.AlterModelOptions(
            name='thana',
            options={},
        ),
        migrations.RemoveField(
            model_name='cityslide',
            name='color',
        ),
        migrations.RemoveField(
            model_name='cityslide',
            name='description',
        ),
        migrations.RemoveField(
            model_name='cityslide',
            name='subtitle',
        ),
        migrations.RemoveField(
            model_name='product',
            name='features',
        ),
        migrations.RemoveField(
            model_name='productfeature',
            name='image',
        ),
        migrations.AddField(
            model_name='city',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='city',
            name='image',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='cityslide',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='productfeature',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='productfeature',
            name='icon',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='productfeature',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='techspec',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='city',
            name='slug',
            field=models.SlugField(max_length=120, unique=True),
        ),
        migrations.AlterField(
            model_name='cityslide',
            name='image',
            field=models.URLField(),
        ),
        migrations.AlterField(
            model_name='citystats',
            name='installations',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='citystats',
            name='rating',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=3),
        ),
        migrations.AlterField(
            model_name='citystats',
            name='users',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='techspec',
            name='details',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='techspec',
            name='icon_name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='address',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='completed_jobs',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='pin',
            field=models.CharField(blank=True, default='', max_length=6),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='qr_code',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(choices=[('customer', 'Customer'), ('provider', 'Service Provider'), ('admin', 'Admin')], default='customer', max_length=20),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='service_area_district',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='service_area_division',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='service_area_thana',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='support_link',
            field=models.URLField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='auth.user'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='verification_code',
            field=models.CharField(blank=True, default='', max_length=6),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='verification_token',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]