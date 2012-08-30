# Create your views here.
from django.http import HttpResponse
import jsonpickle

def convert_to_json_response(result):
    return HttpResponse(jsonpickle.encode(result, unpicklable=False), content_type='application/json; charset=utf-8')