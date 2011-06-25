from django.contrib.gis import admin
from wifi.models import Hotspot, State, City
from wifi.conf import settings
from wifi.forms import HotspotAdminForm

# Abstract settings for possible use in future ModelAdmin classes
class OpenlayersMixin (object):
    map_width = 800
    map_height = 400
    openlayers_url = "/static/openlayers-2.10/OpenLayers.js"
    #default_lat = 40
    #default_lon = -95
    default_lat = settings.DEFAULT_LAT
    default_lon = settings.DEFAULT_LON

class HotspotAdmin (OpenlayersMixin, admin.OSMGeoAdmin):
    form = HotspotAdminForm

    list_display = ["name", "address", "restricted", "status", "geometry"]
    list_filter = ["restricted", "status"]
    search_fields = ["name", "address"]
    fieldsets = (
        ("Hotspot Information", {"fields": ["name", "address", "phone", "description", "restricted"]}),
        ("Location Information", {"fields": ["in_city", "geometry"]}),
        ("Publication Status", {"fields": ["status"]}),
    )

class StateAdmin (admin.ModelAdmin):
    pass

class CityAdmin (admin.ModelAdmin):
    pass

admin.site.register (Hotspot, HotspotAdmin)
admin.site.register (State, StateAdmin)
admin.site.register (City, CityAdmin)

