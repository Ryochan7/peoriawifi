import re
from geopy import geocoders
from django import forms
from django.contrib.gis.geos import Point
from wifi.models import Hotspot
from wifi.conf import settings

class HotspotAdminForm (forms.ModelForm):
    class Meta (object):
        model = Hotspot

    def clean (self):
        temp_point = None
        address = self.cleaned_data.get ("address")
        # Attempt to auto-plot point on map if not already done
        if address and not self.cleaned_data.get ("geometry"):
            g = geocoders.Google (api_key=settings.settings.GOOGLE_MAPS_API_KEY)
            try:
                temp_point = g.geocode (self.cleaned_data["address"])
            except ValueError as exception:
                self._errors["address"] = self.error_class ([exception.message])
            except geocoders.GQueryError as exception:
                self._errors["address"] = self.error_class (["Could not find a corresponding addresss"])
            finally:
                if temp_point:
                    self.cleaned_data["geometry"] = Point (temp_point[1][1], temp_point[1][0])

        return self.cleaned_data

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

