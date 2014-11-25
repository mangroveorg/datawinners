from django.http import HttpResponse
from django_digest.decorators import httpdigest
from datawinners.dataextraction.helper import  encapsulate_data_for_form, convert_to_json_file_download_response
from datawinners.dataextraction.helper import generate_filename, check_date_format
from datawinners.main.database import get_database_manager
from datawinners.submission.models import DatawinnerLog
from datawinners.utils import get_organization
from django.db.models import Q
import operator
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
def get_failed_submissions(request):
    organization = get_organization(request)
    start_date = request.GET.get('start_date') if check_date_format(request.GET.get('start_date')) else None
    end_date = request.GET.get('end_date') if check_date_format(request.GET.get('end_date')) else None
    to_number = request.GET.get('to_number')
    
    criteria = [Q(organization=organization)]

    if start_date is not None:
        criteria.append(Q(created_at__gte=datetime.strptime(start_date, '%d-%m-%Y')))

    if end_date is not None:
        criteria.append(Q(created_at__lte=datetime.strptime(end_date + " 23:59:59", '%d-%m-%Y %H:%M:%S')))

    if to_number is not None:
        criteria.append(Q(to_number=to_number))

    failed_submissions = list(DatawinnerLog.objects.filter(reduce(operator.and_, criteria))
                              .extra(select={'submission_date': 'created_at'})
                              .values('from_number', 'to_number', 'message', 'error', 'submission_date')
                              .order_by('created_at')
                              )
    if len(failed_submissions):
        failed_submissions_dict = {"message": "You can access the data in submissions field.", "submissions": failed_submissions, "success": True}
    else:
        failed_submissions_dict = {"message": "No failed submissions available", "submissions": [], "success": False}

    return convert_to_json_file_download_response(failed_submissions_dict, "failed_submissions")










