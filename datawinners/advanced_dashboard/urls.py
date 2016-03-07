from django.conf.urls.defaults import patterns, url
from datawinners.advanced_dashboard.views import advanced_dashboard

urlpatterns = patterns('',
                       url(r'^advanced_dashboard/$', advanced_dashboard,
                           name='advanced_dashboard'),
                       )
