from wifi.models import City

def featured_cities (request):
    return {
        "featured_cities": City.objects.filter (id__in=(1, 2)),
    }
