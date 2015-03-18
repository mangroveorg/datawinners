import json
from django.http import HttpResponse


def registered_ds_count(request):
    return HttpResponse(json.dumps([{'name': 'questionnaire1', 'id': "q1", 'ds-count': 12},
                                    {'name': 'questionnaire2', 'id': "q2", 'ds-count': 30}]))