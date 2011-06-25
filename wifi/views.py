# Create your views here.
from django.views.generic import TemplateView, ListView
from django.contrib.gis.maps.google.gmap import GoogleMap
from django.contrib.gis.maps.google.overlays import GMarker, GEvent
from wifi.models import Hotspot
from wifi.conf import settings

class WifiIndexView (ListView):
    template_name = "base.html"
    queryset = object_list = Hotspot.objects.all ()

    def get (self, request, *args, **kwargs):
        markers = []
        for hotspot in self.queryset:
            marker = GMarker (hotspot.geometry, title=hotspot.name)
            markers.append (marker)

        google_map = GoogleMap (center=(settings.DEFAULT_LAT, settings.DEFAULT_LON), markers=markers)
        
        context = self.get_context_data (object_list=self.queryset, google_map=google_map)
        return self.render_to_response (context)

class HotspotDetailsView (TemplateView):
    template_name = "wifi/details.html"


