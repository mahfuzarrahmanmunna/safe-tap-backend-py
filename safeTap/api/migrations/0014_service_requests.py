from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_userprofile_created_at_userprofile_nid_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('problem_description', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('assigned', 'Assigned'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_requests', to='auth.user')),
                ('technician', models.ForeignKey(blank=True, limit_choices_to={'profile__role': 'servicer'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_requests', to='auth.user')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ServiceRequestImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='service_requests/images/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('service_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='api.servicerequest')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceRequestVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video', models.FileField(upload_to='service_requests/videos/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('service_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='api.servicerequest')),
            ],
        ),
    ]
