# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.main.utils import get_database_manager
import helper
from mangrove.datastore.entity import get_entities_by_type

def map_entities(request):
    entity_list = get_entities_by_type(get_database_manager(request), request.GET['id'])
    location_geojson = helper.create_location_geojson(entity_list)
    return HttpResponse(location_geojson)


def render_map(request):
    return render_to_response('maps/entity_map.html', context_instance=RequestContext(request))
