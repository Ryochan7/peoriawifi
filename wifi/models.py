#from django.db import models
from django.contrib.gis.db import models

class Hotspot (models.Model):
    name = models.CharField (max_length=100)
    description = models.TextField ()
    geometry = models.PointField (srid=4326)
    objects = models.GeoManager ()

    def __unicode__ (self):
        return self.name


#class Zipcodes (models.Model):
#    code = models.CharField (max_length=5)
#    geometry = models.PolygonField ()
#    objects = models.GeoManager ()

#    def __unicode__ (self):
#        return self.code

