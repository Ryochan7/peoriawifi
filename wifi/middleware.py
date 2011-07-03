from wifi.forms import HotspotFilterForm

class FilterFormMiddleware (object):
    def process_request (self, request):
        form = HotspotFilterForm (request.GET)
        request.filter_form = form
        return

