from django import template
from django.conf import settings
from wifi.models import Hotspot
register = template.Library ()

def featured_wifi_spot ():
    return {"hotspot": Hotspot.objects.get (id=7),
        "STATIC_URL": settings.STATIC_URL}

def dude_filtered_url (context, status):
    stuff = ""
    if "request" in context:
        request = context["request"]
        getvars = request.GET.copy ()
        getvars["free"] = status
        #print getvars
        #print stuff
        stuff = getvars.urlencode ()
        return stuff

    return stuff

register.simple_tag (takes_context=True)(dude_filtered_url)

register.inclusion_tag ("wifi/templatetags/featured_hotspot.html")(featured_wifi_spot)

