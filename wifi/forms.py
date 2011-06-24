import re
from django import forms
from wifi.models import Hotspot

class HotspotAdminForm (forms.ModelForm):
    class Meta (object):
        model = Hotspot

    def clean_phone (self):
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

