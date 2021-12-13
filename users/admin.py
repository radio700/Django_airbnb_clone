from django.contrib import admin
from .models import User

# Register your models here.

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    """" custom user admin """
    list_display = ('username','gender','language','currency','is_superhost')
    list_filter = ("language","is_superhost","currency")