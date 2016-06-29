from django.conf.urls.defaults import patterns

from datawinners.public.views import geo_json_for_entity, render_map

urlpatterns = patterns('',
    (r'^public/get_geojson/(?P<entity_type>.+?)$', geo_json_for_entity),
    (r'^public/maps/(?P<share_token>.+?)$', render_map)
)
