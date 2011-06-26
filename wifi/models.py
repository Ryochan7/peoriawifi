#from django.db import models
from django.contrib.gis.db import models
from sorl.thumbnail import ImageField
from taggit.managers import TaggableManager

class State (models.Model):
    name = models.CharField (max_length=200)

    def __unicode__ (self):
        return self.name

class City (models.Model):
    name = models.CharField (max_length=200)
    in_state = models.ForeignKey (State)

    def __unicode__ (self):
        return u"{0}, {1}".format (self.name, self.in_state.name)

    class Meta (object):
        verbose_name_plural = "Cities"

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
    in_city = models.ForeignKey (City)
    source_image = ImageField (upload_to="hotspot_images", max_length=256, blank=True)
    tags = TaggableManager ()
    # blank and null must be used or widget validation will raise an error on blank
    geometry = models.PointField (srid=4326, blank=True, null=True, help_text="If no point is provided, the address field will be used to find a point from Google Maps")
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

