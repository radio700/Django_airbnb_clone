from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.


# @admin.register(User)
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
                )
            },
        ),
    )
    # list_display = ('username','gender','language','currency','is_superhost')
    # list_filter = ("language","is_superhost","currency")

admin.site.register(User,CustomUserAdmin)