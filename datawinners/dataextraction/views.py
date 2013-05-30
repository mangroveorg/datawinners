from django.http import HttpResponse
from django_digest.decorators import httpdigest
from dataextraction.helper import  encapsulate_data_for_subject, encapsulate_data_for_form, convert_to_json_file_download_response, generate_filename
from datawinners.main.utils import get_database_manager
from mangrove.form_model.form_model import get_form_model_by_entity_type

@httpdigest
def get_for_subject(request, subject_type, subject_short_code, start_date=None, end_date=None):
    if request.method == 'GET':
        user = request.user
        dbm = get_database_manager(user)
        subject_type = subject_type.lower()
        data_for_subject = encapsulate_data_for_subject(dbm, subject_type, subject_short_code, start_date, end_date)
        return convert_to_json_file_download_response(data_for_subject, generate_filename('%s_%s' %(subject_type,subject_short_code), start_date, end_date))
    return HttpResponse("Error. Only support GET method.")

@httpdigest
def get_for_form(request, form_code, start_date=None, end_date=None):
    if request.method == 'GET':
        user = request.user
        dbm = get_database_manager(user)
        data_for_form = encapsulate_data_for_form(dbm, form_code, start_date, end_date)
        return convert_to_json_file_download_response(data_for_form, generate_filename(form_code, start_date, end_date))
    return HttpResponse("Error. Only support GET method.")

@httpdigest
def get_registered_data(request, subject_type, start_date=None, end_date=None):
    manager = get_database_manager(request.user)
    form_model = get_form_model_by_entity_type(manager,[subject_type])
    response = get_for_form(request, form_model.form_code, start_date, end_date)
    return response