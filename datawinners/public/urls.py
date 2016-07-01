from django.conf.urls.defaults import patterns

from datawinners.public.views import render_map

urlpatterns = patterns('',
    (r'^public/maps/(?P<share_token>.+?)$', render_map)
)
