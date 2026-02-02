from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_service_requests'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(max_length=50, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Work Category',
                'verbose_name_plural': 'Work Categories',
            },
        ),
        migrations.CreateModel(
            name='WorkAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('client_name', models.CharField(max_length=200)),
                ('client_phone', models.CharField(blank=True, max_length=15)),
                ('client_email', models.EmailField(blank=True, max_length=254)),
                ('client_address', models.TextField(blank=True)),
                ('division', models.CharField(blank=True, max_length=100)),
                ('district', models.CharField(blank=True, max_length=100)),
                ('thana', models.CharField(blank=True, max_length=100)),
                ('full_address', models.TextField(blank=True)),
                ('scheduled_date', models.DateTimeField(null=True, blank=True)),
                ('estimated_duration', models.CharField(blank=True, max_length=100)),
                ('status', models.CharField(default='pending', max_length=20, choices=[('pending', 'Pending'), ('assigned', 'Assigned'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')])),
                ('priority', models.CharField(default='medium', max_length=10, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')])),
                ('estimated_cost', models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)),
                ('actual_cost', models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(null=True, blank=True)),
                ('admin_notes', models.TextField(blank=True)),
                ('technician_notes', models.TextField(blank=True)),
                ('assigned_to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assignments', to='api.userprofile')),
                ('assigned_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_assignments', to='auth.user')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.workcategory')),
            ],
            options={
                'verbose_name': 'Work Assignment',
                'verbose_name_plural': 'Work Assignments',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AssignmentHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('old_status', models.CharField(blank=True, max_length=20)),
                ('new_status', models.CharField(blank=True, max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='api.workassignment')),
                ('changed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
            ],
            options={
                'verbose_name': 'Assignment History',
                'verbose_name_plural': 'Assignment Histories',
                'ordering': ['-timestamp'],
            },
        ),
    ]
