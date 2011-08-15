from settings.common import *
# Remove database settings imported from common.py. Will cause Django
# to produce an error if DATABASES is not configured in secrets.py
DATABASES = {
}
from settings.secrets import *
DATABASES = DATABASES_PRODUCTION

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "http://peoriawifi.ryochan7.com/media/"
STATIC_URL = "/static/"
ADMIN_MEDIA_PREFIX = "/static/admin/"

