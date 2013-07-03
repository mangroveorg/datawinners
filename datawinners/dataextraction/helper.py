from datetime import datetime
import cStringIO
from django.http import HttpResponse
import jsonpickle
from django.utils.translation import gettext as _
from mangrove.datastore.entity import get_by_short_code_include_voided
from mangrove.datastore.entity_type import entity_type_already_defined
from mangrove.errors.MangroveException import DataObjectNotFound, FormModelDoesNotExistsException
from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.utils.dates import convert_date_string_in_UTC_to_epoch
from datawinners.dataextraction.models import DataExtractionResult


def get_data_for_subject(dbm, subject_type, subject_short_code, start_date=None, end_date=None):
    start = convert_date_string_to_UTC(start_date)
    end = convert_date_string_to_UTC(end_date)

    start_key = [[subject_type], subject_short_code, start] if start is not None else [[subject_type],
                                                                                       subject_short_code]
    end_key = [[subject_type], subject_short_code, end] if end is not None else [[subject_type], subject_short_code, {}]

    rows = dbm.load_all_rows_in_view('by_entity_type_and_entity_id', startkey=start_key, endkey=end_key)

    return [row["value"] for row in rows]


def get_data_for_form(dbm, form_code, start_date=None, end_date=None):
    start = convert_date_string_to_UTC(start_date)
    end = convert_date_string_to_UTC(end_date)

    start_key = [form_code, start] if start is not None else [form_code]
    end_key = [form_code, end] if end is not None else [form_code, {}]

    rows = dbm.load_all_rows_in_view('form_data_by_form_code_time', startkey=start_key, endkey=end_key)

    return [row["value"] for row in rows]


def generate_filename(main, start_date=None, end_date=None):
    if start_date is None:
        return main
    elif end_date is None:
        return '%s_%s' % (main, start_date)
    return '%s_%s_%s' % (main, start_date, end_date)


def encapsulate_data_for_subject(dbm, subject_type, subject_short_code, start_date=None, end_date=None):
    result = validate_for_subject(dbm, subject_type, subject_short_code, start_date, end_date)
    if not result.success:
        return result
    result.submissions = get_data_for_subject(dbm, subject_type, subject_short_code, start_date, end_date)
    if not result.submissions:
        result.message = _("No submission under this subject during this period.")
    return result


def encapsulate_data_for_form(dbm, form_code, start_date=None, end_date=None):
    result = validate_for_form(dbm, form_code, start_date, end_date)
    if not result.success:
        return result
    result.submissions = get_data_for_form(dbm, form_code, start_date, end_date)
    if not result.submissions:
        result.message = _("No submission under this questionnaire during this period.")
    return result


def validate_for_form(dbm, form_code, start_date=None, end_date=None):
    result = DataExtractionResult()
    if not check_if_form_exists(dbm, form_code):
        result.success = False
        result.message = _("Questionnaire code [%s] does not existed.") % form_code
        return result
    result = validate_date(result, start_date, end_date)
    if not result.success:
        return result
    return result


def validate_for_subject(dbm, subject_type, subject_short_code, start_date=None, end_date=None):
    result = DataExtractionResult()
    if not entity_type_already_defined(dbm, [subject_type]):
        result.success = False
        result.message = _("Subject type [%s] is not defined.") % subject_type
        return result
    if not check_if_subject_exists(dbm, subject_short_code, [subject_type]):
        result.success = False
        result.message = _("Subject [%s] is not registered.") % subject_short_code
        return result
    result = validate_date(result, start_date, end_date)
    if not result.success:
        return result
    return result


def validate_date(result, start_date, end_date):
    if not check_start_and_end_date_format(start_date, end_date):
        result.success = False
        result.message = _("The format of start and end date should be DD-MM-YYYY. Example: 25-12-2011")
        return result
    if not check_start_before_end(start_date, end_date):
        result.success = False
        result.message = _("Start date must before end date.")
        return result
    return result


def check_start_before_end(start_date, end_date):
    if start_date is None:
        return True
    elif end_date is None:
        return True
    return convert_date_string_to_UTC(start_date) <= convert_date_string_to_UTC(end_date)


def check_start_and_end_date_format(start_date, end_date):
    return check_date_format(start_date) & check_date_format(end_date)


def check_date_format(date):
    if date is None:
        return True
    try:
        datetime.strptime(date, '%d-%m-%Y')
    except ValueError:
        return False
    return True


def check_if_subject_exists(dbm, subject_short_code, subject_type):
    try:
        get_by_short_code_include_voided(dbm, subject_short_code, subject_type)
        return True
    except DataObjectNotFound:
        return False


def check_if_form_exists(dbm, form_code):
    try:
        get_form_model_by_code(dbm, form_code)
        return True
    except FormModelDoesNotExistsException:
        return False


def convert_to_json_response(result, status_code=200):
    return HttpResponse(jsonpickle.encode(result, unpicklable=False), content_type='application/json; charset=utf-8',
                        status=status_code)


def convert_to_json_file_download_response(result, file_name):
    json_str = jsonpickle.encode(result, unpicklable=False)
    json_file = cStringIO.StringIO()
    json_file.write(json_str)
    response = HttpResponse(json_str, content_type='application/json; charset=utf-8')
    response['Content-Length'] = json_file.tell()
    response['Content-Disposition'] = 'attachment; filename=%s.json' % file_name
    json_file.close()
    return response


def convert_date_string_to_UTC(date_string):
    if date_string is None:
        return None
    return convert_date_string_in_UTC_to_epoch("%s %s" % (date_string, '00:00:00'))