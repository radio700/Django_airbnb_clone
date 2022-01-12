from django.db import models
from . import managers

# Create your models here.
class TimeStampModel(models.Model):

    """time stamp model"""

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    objects = managers.CustomModelManager()

    class Meta:
        abstract = True