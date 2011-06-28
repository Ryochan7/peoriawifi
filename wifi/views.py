# Create your views here.
from django.views.generic import (TemplateView, ListView, DetailView,
    FormView, CreateView)
from django.contrib.gis.maps.google.gmap import GoogleMap
from django.contrib.gis.maps.google.overlays import GMarker, GEvent
from django.contrib.gis.geos import Point
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.http import HttpResponseRedirect
from taggit.models import Tag
from geopy import geocoders
from wifi.models import Hotspot, City
from wifi.forms import AddressSearchForm, HotspotAddForm
from wifi.conf import settings

def get_google_hotspot_map (hotspots):
    markers = []
    for hotspot in hotspots:
        marker = GMarker (hotspot.geometry, title=hotspot.name)
        markers.append (marker)

    google_map = GoogleMap (center=(settings.DEFAULT_LAT, settings.DEFAULT_LON),
            markers=markers)
    return google_map


def get_google_address_info (search):
    data = None
    temp_point = None
    CACHE_TIMEOUT = 3600

    if cache.get (search):
        data = cache.get (search)
    else:    
        g = geocoders.Google (api_key=settings.settings.GOOGLE_MAPS_API_KEY)
        try:
            temp_point = g.geocode (search)
        except ValueError as exception:
            data = None
        except geocoders.GQueryError as exception:
            data = None
        finally:
            if temp_point:
                center_point = Point (temp_point[1][1], temp_point[1][0])
                data = center_point
                cache.set (search.replace (" ", "-"),
                    data, CACHE_TIMEOUT)

    return data

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

        search_form = AddressSearchForm ()
        context["google_map"] = google_map
        context["search_form"] = search_form
        return context

class HotspotSearchView (TemplateView):
    http_method_names = ["get"]
    template_name = "wifi/base.html"

    def get (self, request, *args, **kwargs):
        valid_form = False
        if request.GET.get ("search"):
            form = AddressSearchForm (request.GET)
            # Run validation on form to show errors on page
            valid_form = form.is_valid ()
        else:
            form = AddressSearchForm ()

        context = self.get_context_data (search_form=form)
        if valid_form:
            info = get_google_address_info (form.cleaned_data["search"])
            if not info:
                form._errors["search"] = form.error_class (["Data point could not be determined"])
            else:
                context["google_map"].center = info.get_coords ()

        return self.render_to_response (context)

    def get_context_data (self, **kwargs):
        context = super (self.__class__, self).get_context_data (**kwargs)

        hotspots = Hotspot.objects.all ()
        google_map = get_google_hotspot_map (hotspots)

        context["google_map"] = google_map
        context["search_form"] = kwargs.get ("search_form")
        context["hotspot_list"] = hotspots
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

class HotspotAddView (CreateView):
    form_class = HotspotAddForm
    model = Hotspot
    template_name = "wifi/add.html"

