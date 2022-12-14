from django.db import models

# Create your models here.
class Event(models.Model):
    category = models.CharField(max_length=30)
    # TODO: Changee to geopoint column
    # location = models.PointField(srid=4326,dim=2)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    description = models.CharField(max_length=30)