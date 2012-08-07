from django.contrib.auth.models import User
from django.http import HttpResponse
from dataextraction.helper import  encapsulate_data_for_subject, convert_to_json_response, encapsulate_data_for_form
from main.utils import get_database_manager

def get_for_subject(request, subject_type, subject_id, start_date=None, end_date=None):
    if request.method == 'GET':
        user = User.objects.filter(email="tester150411@gmail.com")[0]
        dbm = get_database_manager(user)
        data_for_subject = encapsulate_data_for_subject(dbm, subject_type, subject_id, start_date, end_date)
        return convert_to_json_response(data_for_subject)
    return HttpResponse("Error. Only support GET method.")

def get_for_form(request, form_code, start_date=None, end_date=None):
    if request.method == 'GET':
        user = User.objects.filter(email="tester150411@gmail.com")[0]
        dbm = get_database_manager(user)
        data_for_form = encapsulate_data_for_form(dbm, form_code, start_date, end_date)
        return convert_to_json_response(data_for_form)
    return HttpResponse("Error. Only support GET method.")
