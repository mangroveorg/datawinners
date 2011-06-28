# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
import settings
from django.contrib import admin

urlpatterns = patterns('',
                       (r'', include('datawinners.accountmanagement.urls')),
                       (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
                       (r'', include('datawinners.reporter.urls')),
                       (r'', include('datawinners.reports.urls')),
                       (r'', include('datawinners.admin.urls')),
                       (r'', include('datawinners.project.urls')),
                       (r'', include('datawinners.smstester.urls')),
                       (r'', include('datawinners.submission.urls')),
                       (r'', include('datawinners.maps.urls')),
                       (r'', include('datawinners.subjects.urls')),
                       (r'', include('datawinners.account.urls')),
                       (r'', include('datawinners.datasenders.urls')),
                       (r'', include('datawinners.dashboard.urls')),
                       (r'', include('datawinners.location.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       )
