from django.contrib.gis import admin
from wifi.models import Hotspot

# Abstract settings for possible later use in future models
class OpenlayersMixin (object):
    map_width = 800
    map_height = 400
    openlayers_url = "/static/openlayers-2.10/OpenLayers.js"

class HotspotAdmin (OpenlayersMixin, admin.GeoModelAdmin):
    pass

admin.site.register (Hotspot, HotspotAdmin)

