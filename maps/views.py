# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import helper
from mangrove.datastore.database import get_db_manager
from mangrove.datastore.entity import get_entities_by_type

def map_entities(request):
    #Fetch all entitites of given type
    entity_list = get_entities_by_type(get_db_manager(), ["Water Point"])
    location_geojson=helper.create_location_geojson(entity_list)
    print location_geojson
    return HttpResponse(location_geojson)

def render_map(request):
    return render_to_response('maps/entity_map.html', context_instance=RequestContext(request))
