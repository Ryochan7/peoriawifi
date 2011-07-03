from django import template
from django.conf import settings
from wifi.models import Hotspot
register = template.Library ()

def featured_wifi_spot ():
    
    return {"hotspot": Hotspot.objects.get (id=7),
        "STATIC_URL": settings.STATIC_URL}

register.inclusion_tag ("wifi/templatetags/featured_hotspot.html")(featured_wifi_spot)

