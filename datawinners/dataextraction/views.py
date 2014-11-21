from django.http import HttpResponse

from django_digest.decorators import httpdigest

from datawinners.dataextraction.helper import  encapsulate_data_for_form, convert_to_json_file_download_response, generate_filename, check_start_and_end_date_format, check_date_format

from datawinners.main.database import get_database_manager
from datawinners.utils import get_organization
from datawinners.submission.models import DatawinnerLog
from datetime import datetime


@httpdigest
def get_for_form(request, form_code, start_date=None, end_date=None):
    if request.method == 'GET':
        user = request.user
        dbm = get_database_manager(user)
        data_for_form = encapsulate_data_for_form(dbm, form_code, start_date, end_date)
        return convert_to_json_file_download_response(data_for_form, generate_filename(form_code, start_date, end_date))
    return HttpResponse("Error. Only support GET method.")

@httpdigest
def get_failed_submissions(request, start_date=None, end_date=None):
    organization = get_organization(request)
    check_start_and_end_date_format(start_date, end_date)
    failed_submissions = DatawinnerLog.objects.filter(organization=organization).filter(created_at=datetime.strptime(start_date, '%d-%m-%Y'))
    fs = []
    for all_failed in failed_submissions:
        fs.append(all_failed)
    return convert_to_json_file_download_response(fs, "down")










