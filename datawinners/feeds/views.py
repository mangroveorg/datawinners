from datetime import datetime
import urllib2
from django.conf import settings
from django.http import HttpResponse
from datawinners.dataextraction.helper import  convert_to_json_response
from datawinners.feeds.database import get_feeds_database
from datawinners.feeds.basic_auth import httpbasic

DATE_FORMAT = '%d-%m-%Y %H:%M:%S'

@httpbasic
def feed_entries(request, form_code):
    if not settings.FEEDS_ENABLED:
        return HttpResponse(404)
    if _invalid_form_code(form_code):
        return HttpResponse(content='Invalid form code provided', status=400)
    if invalid_date(request.GET.get('start_date')):
        return HttpResponse(content='Invalid Start Date provided', status=400)
    if invalid_date(request.GET.get('end_date')):
        return HttpResponse(content='Invalid End Date provided', status=400)
    if lesser_end_date(request.GET.get('end_date'),request.GET.get('start_date')):
        return HttpResponse(content='End Date provided is less than Start Date', status=400)

    feed_dbm = get_feeds_database(request.user)
    start_date = _parse_date(request.GET['start_date'])
    end_date = _parse_date(request.GET['end_date'])
    rows = feed_dbm.view.questionnaire_feed(startkey=[form_code, start_date], endkey=[form_code, end_date])
    result = [row['value'] for row in rows]
    return convert_to_json_response(result)


def _is_empty_string(value):
    return value is None or value.strip() == ''


def _invalid_form_code(form_code):
    if _is_empty_string(form_code):
        return True
    return False


def _parse_date(date):
    date_string = urllib2.unquote(date.strip())
    return datetime.strptime(date_string, DATE_FORMAT)


def invalid_date(date_string):
    if _is_empty_string(date_string):
        return True
    try:
        _parse_date(date_string)
    except ValueError:
        return True
    return False

def lesser_end_date(end_date,start_date):
    end_date = _parse_date(end_date)
    start_date = _parse_date(start_date)
    return end_date < start_date
