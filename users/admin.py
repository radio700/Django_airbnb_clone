from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """ " custom user admin"""

    fieldsets = UserAdmin.fieldsets + (
        (
            "Custom profile",
            {
                "fields": (
                    "avatar",
                    "gender",
                    "bio",
                    "birthday",
                    "language",
                    "currency",
                    "is_superhost",
                    "login_method",
                )
            },
        ),
    )

    # list_filter = UserAdmin.list_filter + ("is_superhost")

    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "is_active",
        "language",
        "currency",
        "is_superhost",
        "is_staff",
        "is_superuser",
        "login_method",
    )
