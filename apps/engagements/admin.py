from django.contrib import admin

# Register your models here.
from .models import Engagement, EngagementMessage

admin.site.register(Engagement)
admin.site.register(EngagementMessage)
