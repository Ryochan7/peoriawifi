from django.conf import settings
from django.contrib.sites.models import Site

def site_context (request):
    '''
    A context process to add important site-wide variables to the
    current Context
    '''
    current_site = ""
    try:
        current_site = Site.objects.get_current()
    except Site.DoesNotExist:
        current_site = ""

    return {
        "current_site": current_site,
        "ANALYTICS": settings.ANALYTICS,
    }

