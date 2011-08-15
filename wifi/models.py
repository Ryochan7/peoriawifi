#from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib import admin
from django.core import urlresolvers
from django.conf import settings
 
from django.contrib.gis.db import models
from taggit.managers import TaggableManager
from datetime import datetime

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
        verbose_name_plural = u"Cities"

    @models.permalink
    def get_absolute_url (self):
        return ("wifi_city_hotspots", (), {"city_id": self.id})


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

    name = models.CharField (max_length=100, db_index=True)
    address = models.CharField (max_length=2000)
    phone = models.CharField (max_length=20, blank=True, help_text="Expected format of phone number is xxx-xxx-xxxx.<br/>Example: 309-123-4567")
    restricted = models.BooleanField (default=OPEN, help_text="Does the hotspot require registration and payment?", db_index=True)
    description = models.TextField ()
    status = models.IntegerField (default=UNPUBLISHED, choices=STATUS_CHOICES, db_index=True)
    in_city = models.ForeignKey (City)
    source_image = models.ImageField (upload_to="hotspot_images", max_length=256, blank=True)
    date_added = models.DateTimeField (default=datetime.now)
    google_cid = models.CharField (max_length=20, blank=True, help_text="Enter the cid of the business' page from Google Places")
    tags = TaggableManager ()
    # blank and null must be used or widget validation will raise an error on blank
    geometry = models.PointField (srid=4326, blank=True, null=True, help_text="If no point is provided, the address field will be used to find a point from Google Maps")
    objects = models.GeoManager ()

    def __unicode__ (self):
        return self.name

    @models.permalink
    def get_absolute_url (self):
        return ("wifi_hotspot_details", (), {"pk": self.id})

    @property
    def populated_tags (self):
        if not getattr (self, "current_tags", None):
            self.current_tags = list (self.tags.all ())

        return self.current_tags

    @property
    def edit_link (self):
        url = urlresolvers.reverse ("admin:wifi_hotspot_change",
            args=(self.id,))
        return url


#class Zipcodes (models.Model):
#    code = models.CharField (max_length=5)
#    geometry = models.PolygonField ()
#    objects = models.GeoManager ()

#    def __unicode__ (self):
#        return self.code

