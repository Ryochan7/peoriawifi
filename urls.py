from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.conf import settings
from wifi.views import (WifiIndexView, HotspotSearchView, HotspotDetailsView,
    HotspotListView, HotspotTaggedView, HotspotAddView)

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'peoriawifi.views.home', name='home'),
    # url(r'^peoriawifi/', include('peoriawifi.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r"^$", WifiIndexView.as_view (), name="home"),
    url(r"^search/$", HotspotSearchView.as_view (), name="wifi_search"),
    url(r"^hotspots/$", HotspotListView.as_view (), name="wifi_hotspot_list"),
    url(r"^hotspot/(?P<pk>\d+)/$", HotspotDetailsView.as_view (), name="wifi_hotspot_details"),
    url(r"^hotspot/tag/(?P<tag_slug>\w+)/$", HotspotTaggedView.as_view (), name="wifi_hotspot_tag"),
    url(r"^hotspot/add/$", login_required (HotspotAddView.as_view ()), name="wifi_add_hotspot"),
)

if settings.DEBUG:
    urlpatterns += patterns ('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )

