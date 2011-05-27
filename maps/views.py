# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.main.utils import get_database_manager
import helper
from mangrove.datastore.entity import get_entities_by_type

def map_entities(request):
    #Fetch all entitites of given type
    entity_list = get_entities_by_type(get_database_manager(request), "Water Point")
    location_geojson=helper.create_location_geojson(entity_list)
    print location_geojson
#    x = json.dumps({ "type": "FeatureCollection",
#  "features": [
#    { "type": "Feature",
#      "geometry": {"type": "Point", "coordinates": [102.0, 0.5]},
#      "properties": {"prop0": "value0"}
#      },
#    { "type": "Feature",
#      "geometry": {
#        "type": "LineString",
#        "coordinates": [
#          [102.0, 0.0], [103.0, 1.0], [104.0, 0.0], [105.0, 1.0]
#          ]
#        },
#      "properties": {
#        "prop0": "value0",
#        "prop1": 0.0
#        }
#      },
#    { "type": "Feature",
#       "geometry": {
#         "type": "Polygon",
#         "coordinates": [
#           [ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0],
#             [100.0, 1.0], [100.0, 0.0] ]
#           ]
#       },
#       "properties": {
#         "prop0": "value0",
#         "prop1": {"this": "that"}
#         }
#       }
#     ]
#   }
#)
#    print x
    return HttpResponse(location_geojson)
def render_map(request):
    return render_to_response('maps/entity_map.html', context_instance=RequestContext(request))
