from django.db import models
from django.conf import settings

from apps.customers.models import Customer


class Engagement(models.Model):

    TYPE_CHOICES = [
        ('DM', 'Direct Message'),
        ('MENTION', 'Mention'),
        ('POST_REPLY', 'Post Reply'),
    ]

    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]

    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('AI_REVIEW', 'AI Review'),
        ('ASSIGNED', 'Assigned'),
        ('CLOSED', 'Closed'),
    ]

    CATEGORY_CHOICES = [
        ('General', 'General'),
        ('Overcharge', 'Overcharge'),
        ('Billing', 'Billing'),
        ('Refund', 'Refund'),
        ('Technical Issue', 'Technical Issue'),
        ('Account Support', 'Account Support'),
        ('Complaint', 'Complaint'),
        ('General Inquiry', 'General Inquiry'),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='engagements'
    )

    engagement_type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES
    )

    external_id = models.CharField(
        max_length=255,
        unique=True
    )

    content = models.TextField()

    ai_response = models.TextField(
        null=True,
        blank=True
    )

    final_response = models.TextField(
        null=True,
        blank=True
    )

    priority = models.CharField(
        max_length=50,
        choices=PRIORITY_CHOICES,
        default='Medium'
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        null=True,
        blank=True,
        default='General'
    )
    sla = models.DateTimeField(
        null=True,
        blank=True,
        auto_now=True
    )


    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='NEW'
    )

    is_auto_replied = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    request_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        editable=False
    )

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        super().save(*args, **kwargs)

        if is_new and not self.request_number:
            self.request_number = f'REQ{self.pk:04d}'
            super().save(update_fields=['request_number'])


    def __str__(self):
        return f"{self.customer.username} - {self.engagement_type}"


class EngagementMessage(models.Model):

    SENDER_CHOICES = [
        ('CUSTOMER', 'Customer'),
        ('AGENT', 'Agent'),
        ('SYSTEM', 'System'),
    ]

    engagement = models.ForeignKey(
        Engagement,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    sender_type = models.CharField(
        max_length=20,
        choices=SENDER_CHOICES
    )

    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['created_at', 'id']

    def __str__(self):
        return f"{self.engagement.request_number} - {self.sender_type}"
