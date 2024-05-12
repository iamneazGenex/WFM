from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import *

# Register your models here.


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = (
        "email",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "email",
        "is_staff",
        "is_active",
    )
    fieldsets = (
        (None, {"fields": ["email", "password"]}),
        ("Personal Info", {"fields": ["name", "employee_id", "system_id"]}),
        (
            "Permissions",
            {"fields": ["is_staff", "is_active", "groups", "user_permissions"]},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Process)
admin.site.register(Employee)
admin.site.register(Supervisor)
admin.site.register(Site)
admin.site.register(LOB)
admin.site.register(WorkRole)
admin.site.register(Skill)
