# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.main.utils import get_database_manager
from datawinners.project.models import Project
from django.conf import settings
import helper
from mangrove.datastore.entity import get_by_short_code
from mangrove.datastore.queries import get_entities_by_type


def map_entities(request):
    dbm = get_database_manager(request.user)
    project = Project.load(dbm.database, request.GET['project_id'])
    if project.is_activity_report():
        entity_list = [get_by_short_code(dbm, short_code, ["reporter"]) for short_code in project.data_senders]
    else:
        entity_list = get_entities_by_type(dbm, request.GET['id'])
    location_geojson = helper.create_location_geojson(entity_list)
    return HttpResponse(location_geojson)

def render_map(request):
    map_api_key = settings.API_KEYS[request.META['HTTP_HOST']]
    return render_to_response('maps/entity_map.html', {'map_api_key': map_api_key},context_instance=RequestContext(request))
