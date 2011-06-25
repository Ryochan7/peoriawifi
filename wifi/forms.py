import re
from geopy import geocoders
from django import forms
from django.contrib.gis.geos import Point
from wifi.models import Hotspot
from wifi.conf import settings

class HotspotAdminForm (forms.ModelForm):
    temp_point = None

    class Meta (object):
        model = Hotspot

    def clean (self):
        # Auto-plot point on map if not already done
        if self.temp_point and not self.cleaned_data.get ("geometry"):
            self.cleaned_data["geometry"] = Point (self.temp_point[1][1], self.temp_point[1][0])

        self.temp_point = None
        return self.cleaned_data

    def clean_address (self):
        g = geocoders.Google (api_key=settings.settings.GOOGLE_MAPS_API_KEY)
        try:
            self.temp_point = g.geocode (self.cleaned_data["address"])
        except ValueError as exception:
            raise forms.ValidationError (exception.message)
        except geocoders.GQueryError as exception:
            raise forms.ValidationError ("Could not find a corresponding addresss")
        
        return self.cleaned_data["address"]

    def clean_phone (self):
        # Skip if blank
        if not self.cleaned_data["phone"]:
            return self.cleaned_data["phone"]

        regex = re.compile(r"""^1?
                (\d{3})     # area code is 3 digits (e.g. '800')
                \D*         # optional separator is any number of non-digits
                (\d{3})     # trunk is 3 digits (e.g. '555')
                \D*         # optional separator
                (\d{4})     # rest of number is 4 digits (e.g. '1212')
                $           # end of string
                """, re.VERBOSE)

        match = regex.match (self.cleaned_data["phone"])
        custom = None
        if match:
            custom = "-".join (match.groups ())
        else:
            raise forms.ValidationError ("Phone number is not in the proper format")
        return custom

