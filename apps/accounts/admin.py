from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms

from .models import User, RoutingGroup, RoutingAttribute, SupervisorScope
# Register your models here.

# admin.site.register(User, UserAdmin)
#
class CustomUserChangeForm(forms.ModelForm):
    routing_groups = forms.ModelMultipleChoiceField(
        queryset=RoutingGroup.objects.all(),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple("Routing Groups", False),
    )

    class Meta:
        model = User
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields["routing_groups"].initial = self.instance.routing_groups.all()

    def save(self, commit=True):
        user = super().save(commit=commit)

        if user.pk:
            user.routing_groups.set(self.cleaned_data["routing_groups"])

        return user

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm

    fieldsets = UserAdmin.fieldsets + (
        ("Team Management", {
            "fields": ("supervisor", "routing_groups"),
        }),
    )


@admin.register(RoutingAttribute)
class RoutingAttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "attribute_type", "is_active")
    list_filter = ("attribute_type", "is_active")
    search_fields = ("name", "code")


@admin.register(SupervisorScope)
class SupervisorScopeAdmin(admin.ModelAdmin):
    list_display = ("supervisor", "created_by", "created_at", "updated_at")
    search_fields = ("supervisor__username", "supervisor__email")
    filter_horizontal = ("attributes",)


@admin.register(RoutingGroup)
class RoutingGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "supervisor", "is_default", "is_active", "created_at")
    list_filter = ("supervisor", "is_default", "is_active")
    search_fields = ("name", "supervisor__username")
    filter_horizontal = ("attributes", "users")