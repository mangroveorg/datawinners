import json
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from dataextraction.helper import get_data_by_subject
from main.utils import get_database_manager

def get_by_subject(request, subject_type, subject_id):
    user = User.objects.filter(email="tester150411@gmail.com")[0]
    dbm = get_database_manager(user)
    data_by_subject = get_data_by_subject(dbm, subject_type, subject_id)
    return HttpResponse(json.dumps(data_by_subject, cls=DjangoJSONEncoder), content_type='application/json; charset=utf-8')