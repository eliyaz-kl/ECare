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

    supervisor = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="team_members"
    )

    class Meta:
        db_table = 'users'

class RoutingAttribute(models.Model):
    class AttributeType(models.TextChoices):
        LANGUAGE = "LANGUAGE", "Language"
        CHANNEL = "CHANNEL", "Channel"
        REQUEST_TYPE = "REQUEST_TYPE", "Request Type"

    attribute_type = models.CharField(
        max_length=20,
        choices=AttributeType.choices
    )
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "routing_attributes"
        unique_together = ("attribute_type", "code")

    def __str__(self):
        return f"{self.get_attribute_type_display()} | {self.name}"

class SupervisorScope(models.Model):
    supervisor = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="supervisor_scope"
    )
    attributes = models.ManyToManyField(
        RoutingAttribute,
        related_name="supervisor_scopes"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_supervisor_scopes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "supervisor_scopes"

    def __str__(self):
        return f"Scope for {self.supervisor.username}"

class RoutingGroup(models.Model):
    supervisor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="managed_routing_groups"
    )
    name = models.CharField(max_length=100)
    attributes = models.ManyToManyField(
        RoutingAttribute,
        related_name="routing_groups"
    )
    users = models.ManyToManyField(
        User,
        blank=True,
        related_name="routing_groups"
    )
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "routing_groups"
        unique_together = ("supervisor", "name")

    def __str__(self):
        return self.name