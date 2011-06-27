# Create your views here.
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.gis.maps.google.gmap import GoogleMap
from django.contrib.gis.maps.google.overlays import GMarker, GEvent
from django.shortcuts import get_object_or_404
from taggit.models import Tag
from wifi.models import Hotspot
from wifi.conf import settings

class WifiIndexView (ListView):
    template_name = "base.html"
    queryset = Hotspot.objects.all ().select_related (depth=1)

    def get_context_data (self, **kwargs):
        context = super (self.__class__, self).get_context_data (**kwargs)
        markers = []
        for hotspot in self.object_list:
            marker = GMarker (hotspot.geometry, title=hotspot.name)
            markers.append (marker)

        google_map = GoogleMap (center=(settings.DEFAULT_LAT, settings.DEFAULT_LON),
            markers=markers)

        context["google_map"] = google_map
        return context


class HotspotDetailsView (DetailView):
    model = Hotspot
    template_name = "wifi/details.html"

    def get_context_data (self, **kwargs):
        context = super (self.__class__, self).get_context_data (**kwargs)
        hotspot = self.object
        markers = []
        marker = GMarker (hotspot.geometry, title=hotspot.name)
        markers.append (marker)

        google_map = GoogleMap (center=(settings.DEFAULT_LAT,
            settings.DEFAULT_LON), markers=markers)
        context["google_map"] = google_map
        return context

class HotspotListView (ListView):
    model = Hotspot
    template_name = "wifi/list.html"

class HotspotTaggedView (ListView):
    template_name = "wifi/tagged.html"

    def get_queryset (self):
        tag_slug = self.kwargs.get ("tag_slug")
        return Hotspot.objects.filter (tags__slug=tag_slug)

    def get_context_data (self, **kwargs):
        context = super (self.__class__, self).get_context_data (**kwargs)
        markers = []
        for hotspot in self.object_list:
            marker = GMarker (hotspot.geometry, title=hotspot.name)
            markers.append (marker)

        google_map = GoogleMap (center=(settings.DEFAULT_LAT, settings.DEFAULT_LON),
            markers=markers)

        context["google_map"] = google_map

        tag_slug = self.kwargs.get ("tag_slug")
        tag = get_object_or_404 (Tag, slug=tag_slug)
        context["tag"] = tag
        return context

