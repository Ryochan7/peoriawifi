# Create your views here.
from django.views.generic import TemplateView

class WifiIndexView (TemplateView):
    template_name = "base.html"

class HotspotDetailsView (TemplateView):
    template_name = "wifi/details.html"


