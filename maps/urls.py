# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns
from datawinners.maps.views import map_entities, render_map

urlpatterns = patterns('',
        (r'^get_geojson/entity_type$', map_entities),
        (r'^maps/entity_type$', render_map)
)
