# Create your views here.
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_response_exempt, csrf_view_exempt, csrf_exempt
from django.views.decorators.http import require_http_methods
from datawinners.location.LocationTree import LocationTree, get_locations_for_country


@csrf_response_exempt
@csrf_view_exempt
@require_http_methods(['GET'])
def places  (request):
    query_string=request.GET.get('q')
    print query_string
    location = get_locations_for_country(country="Madagascar",start_with=query_string)
    return HttpResponse("\n".join(location))

