from django.contrib import admin
from . import models

# Register your models here.

@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    """review admin def"""
    pass

    list_display = ("__str__", "rating_average")
    #__str__은 models.py rating_average 위에껄 불러온거다



