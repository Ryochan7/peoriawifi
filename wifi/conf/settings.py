from django.conf import settings

DEFAULT_LAT = getattr (settings, "DEFAULT_LAT", 40.6936488)
DEFAULT_LON = getattr (settings, "DEFAULT_LON", -89.5889864)
GOOGLE_MAPS_API_KEY = getattr (settings, "GOOGLE_MAPS_API_KEY", "")

