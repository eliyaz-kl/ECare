from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('engagements', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EngagementMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_type', models.CharField(choices=[('CUSTOMER', 'Customer'), ('AGENT', 'Agent'), ('SYSTEM', 'System')], max_length=20)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('agent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('engagement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='engagements.engagement')),
            ],
            options={
                'ordering': ['created_at', 'id'],
            },
        ),
    ]
