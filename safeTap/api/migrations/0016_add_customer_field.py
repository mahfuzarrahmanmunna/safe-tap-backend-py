from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_create_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='workassignment',
            name='customer',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, to='api.customer'),
        ),
    ]
