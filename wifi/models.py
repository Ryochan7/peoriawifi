#from django.db import models
from django.contrib.gis.db import models

class Hotspot (models.Model):
    UNPUBLISHED = 0
    PUBLISHED = 1
    REQUIRES_MODERATION = 2

    STATUS_CHOICES = (
        (UNPUBLISHED, "Unpublished"),
        (PUBLISHED, "Published"),
        (REQUIRES_MODERATION, "Requires Moderation"),
    )

    OPEN = False
    RESTRICTED = True
    RESTRICTION_CHOICES = (
        (OPEN, "Open"),
        (RESTRICTED, "Restricted"),
    )

    name = models.CharField (max_length=100)
    address = models.CharField (max_length=2000)
    phone = models.CharField (max_length=20, blank=True, help_text="Expected format of phone number is xxx-xxx-xxxx.<br/>Example: 309-123-4567")
    restricted = models.BooleanField (default=OPEN, choices=RESTRICTION_CHOICES, help_text="Does the hotspot require registration and payment?")
    description = models.TextField ()
    status = models.IntegerField (default=UNPUBLISHED, choices=STATUS_CHOICES)
    geometry = models.PointField (srid=4326)
    objects = models.GeoManager ()

    def __unicode__ (self):
        return self.name

    @models.permalink
    def get_absolute_url (self):
        return ("wifi_hotspot_details", (), {"hotspot_id": self.id})


#class Zipcodes (models.Model):
#    code = models.CharField (max_length=5)
#    geometry = models.PolygonField ()
#    objects = models.GeoManager ()

#    def __unicode__ (self):
#        return self.code

