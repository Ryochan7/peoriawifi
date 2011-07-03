import re
from geopy import geocoders
from geopy.geocoders.google import GQueryError
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
            except GQueryError as exception:
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
                \(?(\d{3})\)?     # area code is 3 digits (e.g. '800')
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

class AddressSearchForm (forms.Form):
    DISTANCE_CHOICES = (
        (1, "1 mile"),
        (5, "5 miles"),
        (10, "10 miles"),
        (25, "25 miles"),
        (50, "50 miles"),
    )
    search = forms.CharField (max_length=1000, help_text="Address or Zipcode", widget=forms.TextInput (attrs={'size': '30'}))
    distance = forms.ChoiceField (choices=DISTANCE_CHOICES, initial=25)
    #restricted = forms.BooleanField (required=False, initial=False, widget=forms.HiddenInput ())

# Used as a validator for the Only Free filter
class HotspotFilterForm (forms.Form):
    DISTANCE_CHOICES = (
        (1, "1 mile"),
        (5, "5 miles"),
        (10, "10 miles"),
        (25, "25 miles"),
        (50, "50 miles"),
    )

    free = forms.BooleanField (initial=False)
    search = forms.CharField (required=False, max_length=1000, help_text="Address or Zipcode", widget=forms.HiddenInput())
    distance = forms.ChoiceField (required=False, choices=DISTANCE_CHOICES, initial=25, widget=forms.HiddenInput ())

class HotspotAddForm (HotspotAdminForm):
    class Meta (object):
        model = Hotspot
        fields = ("name", "address", "phone", "restricted",
            "in_city", "description", "source_image", "tags")

    def save (self, commit=True):
        self.instance.geometry = self.cleaned_data["geometry"]
        return super (self.__class__, self).save (commit)

