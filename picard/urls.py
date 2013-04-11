from django.contrib import admin
from django.conf.urls import patterns, include, url
from django.views.generic.simple import redirect_to

admin.autodiscover()

urlpatterns = patterns('',
    # admin
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    #apps
    (r'^Jan/', include('picard.Jan.urls')),
    # Make Jan default application
    (r'^$', redirect_to, {'url':'/Jan/'}),
)
