# Create your views here.
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_response_exempt, csrf_view_exempt
from django.views.decorators.http import require_http_methods
from datawinners.location.LocationTree import   get_location_groups_for_country
from datawinners.location.utils import map_location_groups_to_categories


@csrf_response_exempt
@csrf_view_exempt
@require_http_methods(['GET'])
def places  (request):
    query_string = request.GET.get('term')
    location_group = get_location_groups_for_country(country="Madagascar", start_with=query_string)
    categories = map_location_groups_to_categories(location_group, country="Madagascar")

    return HttpResponse(json.dumps(categories), mimetype="application/json", content_type="application/json")

