from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('engagements', '0002_engagementmessage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='engagement',
            name='category',
            field=models.CharField(blank=True, choices=[('General', 'General'), ('Overcharge', 'Overcharge'), ('Billing', 'Billing'), ('Refund', 'Refund'), ('Technical Issue', 'Technical Issue'), ('Account Support', 'Account Support'), ('Appreciation', 'Appreciation'), ('Complaint', 'Complaint'), ('General Inquiry', 'General Inquiry')], default='General', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='engagement',
            name='status',
            field=models.CharField(choices=[('NEW', 'New'), ('AUTO_REPLY', 'Auto Reply'), ('AI_REVIEW', 'AI Review'), ('ASSIGNED', 'Assigned'), ('CLOSED', 'Closed')], default='NEW', max_length=50),
        ),
    ]
