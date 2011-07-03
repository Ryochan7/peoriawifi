import re
import logging
from geopy import geocoders
from geopy.geocoders.google import GQueryError
from django import forms
from django.contrib.gis.geos import Point
from wifi.models import Hotspot
from wifi.conf import settings

google_re = re.compile (r"^(?P<address>[\w ]+)(, )?(?P<city>\w+), (?P<state>\w+)(?: )?(?P<zip>\d+)?, (?P<country>\w+)")
logger = logging.getLogger ("wifi.forms")
accepted_zips = ["61601", "61602", "61603", "61604", "61605", "61606", "61607",
    "61612", "61613", "61614", "61615", "61625", "61629", "61630", "61633",
    "61634", "61635", "61636", "61637", "61638", "61639", "61641", "61643",
    "61650", "61651", "61652", "61653", "61654", "61655", "61656"]
accepted_cities = ["peoria, il", "peoria, illinois"]

class HotspotAdminForm (forms.ModelForm):
    class Meta (object):
        model = Hotspot

    def clean (self):
        temp_point = None
        google_match = None
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
                    logging.debug ("Attempt to parse address {0}".format (
                        temp_point[0]))
                    google_match = google_re.match (temp_point[0])
                    if not google_match:
                        self._errors["address"] = self.error_class (
                            ["Google address \"{0}\" does not match regex.".format (
                        temp_point[0]
                        )
                    ])
       
        if google_match:
            if google_match.group ("zip"):
                if google_match.group ("zip") not in accepted_zips:
                    self._errors["address"] = self.error_class (
                        ["Address not in a valid zipcode"]
                    )
            elif google_match.group ("city") and google_match ("state"):
                if ", ".join (
                    [google_match.group ("city").lower (),
                    google_match.group ("state").lower ()]
                    ) not in accepted_cities:

                    self._errors["address"] = self.error_class (
                        ["Address not in a valid city"]
                    )

        
        if self._errors.get ("address", None):
            logging.debug ("Address error on {0}".format (address))
        elif temp_point:
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

    free = forms.BooleanField (initial=False, label="Only Free")
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

