# Create your views here.
from django.views.generic import (TemplateView, ListView, DetailView,
    FormView, CreateView)
from django.contrib.gis.maps.google.gmap import GoogleMap
from django.contrib.gis.maps.google.overlays import GMarker, GEvent, GIcon
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.template import RequestContext
from taggit.models import Tag
from geopy import geocoders
from wifi.models import Hotspot, City
from wifi.forms import AddressSearchForm, HotspotAddForm, HotspotFilterForm
from wifi.conf import settings

def get_google_hotspot_map (hotspots, zoom=None):
    markers = []
    center = (settings.DEFAULT_LON, settings.DEFAULT_LAT)
    for i, hotspot in enumerate (hotspots):
        if hotspot.restricted:
            icon = GIcon ("hotspot{0}".format (i),
                "http://www.google.com/intl/en_us/mapfiles/ms/micons/green-dot.png",
            iconsize=(32,32))
            marker = GMarker (hotspot.geometry, title=hotspot.name, icon=icon)
        else:
            marker = GMarker (hotspot.geometry, title=hotspot.name)

        markers.append (marker)

    num_markers = len (markers)
    if num_markers > 1:
        # Perform calc_zoom
        zoom = None
    elif num_markers == 1:
        # Make point center
        center = hotspots[0].geometry.get_coords ()
        zoom = zoom if zoom else 15

    kwargs = {
        "center": center,
        "markers": markers,
        "zoom": zoom,
    }
    google_map = GoogleMap (**kwargs)
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


class FilteredView (ListView):
    filter_form = None

    def get (self, request, *args, **kwargs):
        self.filter_form = HotspotFilterForm (request.GET)
        return super (FilteredView, self).get (request, *args, **kwargs)

    def get_queryset (self):
        queryset = super (FilteredView, self).get_queryset ()
        if self.filter_form.is_valid ():
            free = self.filter_form.cleaned_data["free"]
            queryset = queryset.filter (restricted=not free)
        return queryset

    def get_context_data (self, **kwargs):
        context = super (FilteredView, self).get_context_data (**kwargs)
        context["filter_form"] = self.filter_form
        if not self.filter_form.is_valid ():
            context["filter_form"] = HotspotFilterForm ()
        return context

class WifiIndexView (ListView):
    template_name = "index.html"
    paginate_by = 2
    center_point = Point (settings.DEFAULT_LON, settings.DEFAULT_LAT, srid=4326)

    def get_queryset (self):
        # Get all Hotspots within 25 miles
        queryset = Hotspot.objects.filter (
            geometry__distance_lte=(self.center_point, D(mi=25))
            ).select_related (depth=2)
        return queryset

    def get_context_data (self, **kwargs):
        context = super (WifiIndexView, self).get_context_data (**kwargs)
        google_map = get_google_hotspot_map (context["object_list"])
        context["google_map"] = google_map

        search_form = AddressSearchForm ()
        context["search_form"] = search_form
        context["filter_form"] = HotspotFilterForm ()
        return context

class HotspotSearchView (ListView):
    http_method_names = ["get"]
    center_point = Point (settings.DEFAULT_LON, settings.DEFAULT_LAT, srid=4326)
    paginate_by = 5
    template_name = "wifi/search.html"
    view_options = {
    }

    def get (self, request, *args, **kwargs):
        valid_form = False
        if request.GET.get ("search") and request.GET.get ("distance"):
            form = AddressSearchForm (request.GET)
            # Run validation on form to show errors on page
            valid_form = form.is_valid ()
        else:
            form = AddressSearchForm ()

        center = None
        search_distance = None
        search = None
        if valid_form:
            info = get_google_address_info (form.cleaned_data["search"])
            search = form.cleaned_data["search"]
            if not info:
                form._errors["search"] = form.error_class (
                    ["Data point could not be determined"]
                )
            else:
                center = info
                search_distance = form.cleaned_data["distance"]

        self.view_options = {
            "center": center,
            "search_distance": search_distance,
            "search_form": form,
            "search": search
        }

        return super (HotspotSearchView, self).get (request, *args, **kwargs)

    def get_queryset (self):
        hotspots = None
        center = self.view_options.get ("center", None)
        search_form = self.view_options.get ("search_form", None)
        search_distance = self.view_options.get ("search_distance", None)
        if center and search_distance:
            hotspots = Hotspot.objects.filter (
                geometry__distance_lte=(center, D(mi=search_distance))
            )
        elif center:
            hotspots = Hotspot.objects.filter (
                geometry__distance_lte=(center,
                D(mi=search_form.fields["distance"].initial))
            )
        else:
            hotspots = Hotspot.objects.none ()
       
        return hotspots

    def get_context_data (self, **kwargs):
        context = super (HotspotSearchView, self).get_context_data (**kwargs)
        hotspots = context["object_list"]
        center = self.view_options.get ("center", None)
        search_form = self.view_options.get ("search_form", None)
        search_distance = self.view_options.get ("search_distance", None)
        search = self.view_options.get ("search", None)

        google_map = get_google_hotspot_map (hotspots, zoom=12)
        if center:
            google_map.center = center.get_coords ()

        context["google_map"] = google_map
        context["search_form"] = search_form
        context["filter_form"] = HotspotFilterForm (
            initial={"search": search, "distance": search_distance}
        )
        return context

class HotspotFilteredView (HotspotSearchView):
    filter_form = None
    
    def get (self, request, *args, **kwargs):
        self.filter_form = HotspotFilterForm (request.GET)
        return super (HotspotFilteredView, self).get (request, *args, **kwargs)

    def get_queryset (self):
        center = self.view_options.get ("center", None)
        if center:
            queryset = super (HotspotFilteredView, self).get_queryset ()
        else:
            queryset = Hotspot.objects.filter (
                geometry__distance_lte=(self.center_point, D(mi=25))
                ).select_related (depth=2)

        if self.filter_form.is_valid ():
            free = self.filter_form.cleaned_data["free"]
            queryset = queryset.filter (restricted=not free)
        return queryset

    def get_context_data (self, **kwargs):
        context = super (HotspotFilteredView, self).get_context_data (**kwargs)
        context["filter_form"] = self.filter_form
        if not self.filter_form.is_valid ():
            context["filter_form"] = HotspotFilterForm ()

        return context

class HotspotDetailsView (DetailView):
    queryset = Hotspot.objects.all ().select_related (depth=2)
    template_name = "wifi/details.html"

    def get_context_data (self, **kwargs):
        context = super (HotspotDetailsView, self).get_context_data (**kwargs)
        hotspot = self.object
        hotspots = [hotspot]
        google_map = get_google_hotspot_map (hotspots)
        context["google_map"] = google_map

        search_form = AddressSearchForm ()
        context["search_form"] = search_form
        return context

class HotspotListView (ListView):
    center_point = Point (settings.DEFAULT_LON, settings.DEFAULT_LAT,
        srid=4326)
    paginate_by = 5
    queryset = Hotspot.objects.filter (
        geometry__distance_lte=(center_point, D(mi=25))
        ).select_related (depth=2)
    template_name = "wifi/list.html"

    def get_context_data (self, **kwargs):
        context = super (HotspotListView, self).get_context_data (**kwargs)
        search_form = AddressSearchForm ()
        context["search_form"] = search_form
        return context

class HotspotCityView (FilteredView):
    paginate_by = 5
    template_name = "wifi/city.html"

    def get_queryset (self):
        city_id = self.kwargs.get ("city_id")
        self.queryset = Hotspot.objects.filter (
            in_city__id=city_id).select_related (depth=2)
        queryset = super (HotspotCityView, self).get_queryset ()
        return queryset

    def get_context_data (self, **kwargs):
        context = super (HotspotCityView, self).get_context_data (**kwargs)
        google_map = get_google_hotspot_map (context["object_list"], zoom=12)
        context["google_map"] = google_map
        city_id = self.kwargs.get ("city_id")
        city = get_object_or_404 (City, id=city_id)
        context["city"] = city

        search_form = AddressSearchForm ()
        context["search_form"] = search_form
        context["filter_form_use_url"] = True
        return context

class HotspotTaggedView (FilteredView):
    template_name = "wifi/tagged.html"
    paginate_by = 5
    center_point = Point (settings.DEFAULT_LON, settings.DEFAULT_LAT, srid=4326)

    def get_queryset (self):
        tag_slug = self.kwargs.get ("tag_slug")
        self.queryset = Hotspot.objects.filter (tags__slug=tag_slug).filter (
            geometry__distance_lte=(self.center_point, D(mi=25))
        )
        queryset = super (HotspotTaggedView, self).get_queryset ()
        return queryset

    def get_context_data (self, **kwargs):
        context = super (HotspotTaggedView, self).get_context_data (**kwargs)
        google_map = get_google_hotspot_map (context["object_list"])
        context["google_map"] = google_map

        tag_slug = self.kwargs.get ("tag_slug")
        tag = get_object_or_404 (Tag, slug=tag_slug)
        context["tag"] = tag

        search_form = AddressSearchForm ()
        context["search_form"] = search_form
        context["filter_form_use_url"] = True
        return context

class HotspotCityTaggedView (HotspotTaggedView):
    def get_queryset (self):
        queryset = super (HotspotCityTaggedView, self).get_queryset ()
        city_id = self.kwargs.get ("city_id")
        queryset = queryset.filter (in_city__id=city_id)
        return queryset

    def get_context_data (self, **kwargs):
        context = super (HotspotCityTaggedView, self).get_context_data (
            **kwargs
        )
        city_id = self.kwargs.get ("city_id")
        city = get_object_or_404 (City, id=city_id)
        context["city"] = city

        search_form = AddressSearchForm ()
        context["search_form"] = search_form
        context["filter_form_use_url"] = True
        return context

class HotspotAddView (CreateView):
    form_class = HotspotAddForm
    model = Hotspot
    template_name = "wifi/add.html"
    
    def get_form_kwargs (self):
        self.object = Hotspot (status=Hotspot.REQUIRES_MODERATION)
        if self.request.user.is_superuser:
            self.object.status = Hotspot.PUBLISHED

        kwargs = super (HotspotAddView, self).get_form_kwargs ()
        return kwargs

    def get_context_data (self, **kwargs):
        context = super (HotspotAddView, self).get_context_data (**kwargs)
        search_form = AddressSearchForm ()
        context["search_form"] = search_form
        context["filter_form"] = HotspotFilterForm ()
        return context

