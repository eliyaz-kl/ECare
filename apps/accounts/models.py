from django.contrib.auth.models import AbstractUser
from django.db import models


# class User(AbstractUser):
#     """
#     Custom User model extending Django's AbstractUser
#     """
#     phone = models.CharField(max_length=15, blank=True, null=True)
#     profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
#     date_of_birth = models.DateField(blank=True, null=True)
#     channels = models.CharField(max_length=255, blank=True, null=True)
#
#     class Meta:
#         db_table = 'users'
#         verbose_name = 'User'
#         verbose_name_plural = 'Users'
#
#     def __str__(self):
#         return self.username



class User(AbstractUser):
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        LUNCH = "LUNCH", "Lunch Break"
        SHORT_BREAK = "SHORT_BREAK", "Short Break"
        PRAYER_BREAK = "PRAYER_BREAK", "Prayer Break"
        MEETING = "MEETING", "Meeting"
        LEAVING = "LEAVING", "Leaving for the Day"
        OFFLINE = "OFFLINE", "Offline"

    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    channels = models.CharField(max_length=255, blank=True, null=True)

    current_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OFFLINE
    )

    status_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
