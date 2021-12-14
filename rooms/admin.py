from django.contrib import admin
from . import models
# Register your models here.

@admin.register(models.RoomType)
class ItemAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Amenity)
class ItemAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Facility)
class ItemAdmin(admin.ModelAdmin):
    pass

@admin.register(models.HouseRule)
class ItemAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Room)
class RoomAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Photo)
class PhotoAdmin(admin.ModelAdmin):
    """ """
    pass