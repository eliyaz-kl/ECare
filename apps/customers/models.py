from django.db import models


class Customer(models.Model):
    PLATFORM_CHOICES = [
        ('X', 'X Platform'),
    ]

    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, default='X')
    external_user_id = models.CharField(max_length=255, unique=True)

    username = models.CharField(max_length=255)

    display_name = models.CharField(max_length=255, null=True, blank=True)

    profile_image = models.URLField(
        null=True,
        blank=True
    )

    followers_count = models.IntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.username
