from django.db import models
from django.contrib.auth.models import User

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

    category = models.TextField(
        null=True,
        blank=True,
        default = 'Overcharge'
    )
    sla = models.DateTimeField(
        null=True,
        blank=True,
        auto_now=True
    )


    assigned_agent = models.ForeignKey(
        User,
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

    def __str__(self):
        return f"{self.customer.username} - {self.engagement_type}"