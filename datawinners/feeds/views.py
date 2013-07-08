from datetime import datetime
import logging
import urllib2
from django.conf import settings
from django.http import HttpResponse
from datawinners.main.database import get_db_manager, get_database_manager
from datawinners.dataextraction.helper import convert_to_json_response
from datawinners.feeds.database import get_feeds_database
from datawinners.feeds.authorization import httpbasic, is_not_datasender
from mangrove.errors.MangroveException import FormModelDoesNotExistsException
from mangrove.form_model.form_model import get_form_model_by_code

DATE_FORMAT = '%d-%m-%Y %H:%M:%S'


@httpbasic
@is_not_datasender
def feed_entries(request, form_code):
    try:
        if not settings.FEEDS_ENABLED:
            return HttpResponse(404)
        if invalid_date(request.GET.get('start_date')):
            return convert_to_json_response({"ERROR_CODE": 102, "ERROR_MESSAGE": 'Invalid Start Date provided'}, 400)
        if invalid_date(request.GET.get('end_date')):
            return convert_to_json_response({"ERROR_CODE": 102, "ERROR_MESSAGE": 'Invalid End Date provided'}, 400)
        if lesser_end_date(request.GET.get('end_date'), request.GET.get('start_date')):
            return convert_to_json_response(
                {"ERROR_CODE": 103, "ERROR_MESSAGE": 'End Date provided is less than Start Date'}, 400)
        if _invalid_form_code(request, form_code):
            return convert_to_json_response({"ERROR_CODE": 101, "ERROR_MESSAGE": 'Invalid form code provided'}, 400)

        feed_dbm = get_feeds_database(request.user)
        start_date = _parse_date(request.GET['start_date'])
        end_date = _parse_date(request.GET['end_date'])
        rows = feed_dbm.view.questionnaire_feed(startkey=[form_code, start_date], endkey=[form_code, end_date],
                                                limit=settings.MAX_FEED_ENTRIES)
        result = [row['value'] for row in rows]
        return convert_to_json_response(result)
    except Exception as e:
        logger = logging.getLogger('datawinners')
        logger.exception(e)
        return HttpResponse(content='Internal Server Error', status=500)


def _is_empty_string(value):
    return value is None or value.strip() == ''


def _invalid_form_code(request, form_code):
    try:
        dbm = get_database_manager(request.user)
        get_form_model_by_code(dbm, form_code)
        return False
    except FormModelDoesNotExistsException as e:
        return True

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


def lesser_end_date(end_date, start_date):
    end_date = _parse_date(end_date)
    start_date = _parse_date(start_date)
    return end_date < start_date
