from django.conf.urls.defaults import patterns
from datawinners.feature_toggle_demo_secured_endpoint.views import secured_view

urlpatterns = patterns('', (r'^secured_view/$', secured_view))
