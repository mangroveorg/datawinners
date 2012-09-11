# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import logging
from babel.dates import format_date
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.utils.translation import ugettext
from accountmanagement.models import NGOUserProfile
from datawinners.scheduler.smsclient import SMSClient
from mangrove.datastore.datadict import create_datadict_type, get_datadict_type_by_slug
from mangrove.datastore.documents import attributes
from mangrove.datastore.entity import get_by_short_code
from mangrove.errors.MangroveException import DataObjectNotFound, FormModelDoesNotExistsException
from mangrove.form_model.field import TextField, IntegerField, DateField, GeoCodeField
from mangrove.form_model.form_model import FormModel, get_form_model_by_code, REPORTER
from mangrove.form_model.validation import  TextLengthConstraint
from mangrove.utils.types import  is_sequence, is_string, sequence_to_str
from mangrove.datastore import aggregrate as aggregate_module
import models
import xlwt
from datetime import datetime
from mangrove.transport.submissions import  Submission, get_submissions
from models import Reminder
from mangrove.transport import Request, TransportInfo
import re

UNKNOW_DATASENDER_NAME = "N/A"

NUMBER_TYPE_OPTIONS = ["Latest", "Sum", "Count", "Min", "Max", "Average"]
MULTI_CHOICE_TYPE_OPTIONS = ["Latest"]
DATE_TYPE_OPTIONS = ["Latest"]
GEO_TYPE_OPTIONS = ["Latest"]
TEXT_TYPE_OPTIONS = ["Latest"]
TEST_FLAG = 'TEST'
SUCCESS_SUBMISSION_LOG_VIEW_NAME = "success_submission_log"

logger = logging.getLogger("datawinners.reminders")

def get_or_create_data_dict(dbm, name, slug, primitive_type, description=None):
    try:
        #  Check if is existing
        ddtype = get_datadict_type_by_slug(dbm, slug)
    except DataObjectNotFound:
        #  Create new one
        ddtype = create_datadict_type(dbm=dbm, name=name, slug=slug,
            primitive_type=primitive_type, description=description)
    return ddtype


def _create_entity_id_question(dbm, entity_id_question_code):
    entity_data_dict_type = get_or_create_data_dict(dbm=dbm, name="eid", slug="entity_id", primitive_type="string",
        description="Entity ID")
    name = ugettext("Which subject are you reporting on?")
    entity_id_question = TextField(name=name, code=entity_id_question_code,
        label=name,
        entity_question_flag=True, ddtype=entity_data_dict_type,
        constraints=[TextLengthConstraint(min=1, max=12)],
        instruction=(ugettext('Answer must be a word %d characters maximum') % 12))
    return entity_id_question

def hide_entity_question(fields):
    return [each for each in fields if not each.is_entity_field]


def is_submission_deleted(submission):
    return submission.is_void() if submission is not None else True

def adapt_submissions_for_template(questions, submissions):
    assert is_sequence(questions)
    assert is_sequence(submissions)
    for s in submissions:
        assert type(s) is Submission and s._doc is not None
    formatted_list = []
    for each in submissions:
        case_insensitive_dict = {key.lower(): value for key, value in each.values.items()}
        formatted_list.append(
            [each.uuid, each.destination, each.source, each.created, each.errors,
             "Success" if each.status else "Error"] +
            ["Yes" if is_submission_deleted(each.data_record) else "No"] + [
            get_according_value(case_insensitive_dict, q) for q in questions])

    return [tuple(each) for each in formatted_list]


def get_according_value(value_dict, question):
    value = value_dict.get(question.code.lower(), '--')
    if value != '--' and question.type in ['select1', 'select']:
        value_list = []
        responses = re.findall(r'[1-9]?[a-z]', value)
        for response in responses:
            value_list.extend([opt['text'][question.language] for opt in question.options if opt['val'] == response])
        return ", ".join(value_list)
    return value


def generate_questionnaire_code(dbm):
    all_projects_count = models.count_projects(dbm)
    code = all_projects_count + 1
    code = "%03d" % (code,)
    while True:
        try:
            get_form_model_by_code(dbm, code)
            code = int(code) + 1
            code = "%03d" % (code,)
        except FormModelDoesNotExistsException:
            break
    return code

def get_headers(form_model):
    prefix = [ _("Submission Date"), _("Data Sender") ]
    if form_model.event_time_question:
        prefix = [_("Reporting Period")] + prefix

    if form_model.entity_type != ['reporter']:
        prefix = [_(form_model.entity_type[0]).capitalize()] + prefix

    return prefix + [field.label[form_model.activeLanguages[0]] for field in form_model.fields[1:] if not field.is_event_time_field]


def get_org_id_by_user(user):
    org_id = NGOUserProfile.objects.get( user=user ).org_id
    return org_id


def get_datasender_by_mobile(dbm, mobile):
    rows = dbm.load_all_rows_in_view( "datasender_by_mobile", startkey=[mobile], endkey=[mobile, {}] )
    return rows[0].key[1:] if len(rows) > 0 else [UNKNOW_DATASENDER_NAME, None]

def get_data_sender(dbm, user, submission):
    submission_source = submission.source
    datasender = ('N/A', None, submission_source)

    if submission.channel == 'sms':
        datasender = tuple(get_datasender_by_mobile( dbm, submission_source ) + [submission_source])
    elif submission.channel == 'web' or submission.channel == 'smartPhone':
            try:
                org_id = get_org_id_by_user( user )
                data_sender = User.objects.get(email=submission_source )
                reporter_id = NGOUserProfile.objects.filter(user=data_sender, org_id=org_id)[0].reporter_id or "admin"
                datasender = (data_sender.get_full_name(), reporter_id, submission_source)
            except:
                pass

    return datasender if datasender[0] != "TEST" else ("TEST","", "TEST")


def case_insensitive_lookup(search_key, dictionary):
    assert isinstance(dictionary, dict)
    for key, value in dictionary.items():
        if key.lower() == search_key.lower():
            return value
    return None

def get_first_element_of_leading_part(dbm, form_model, submission, data_sender):
    try:
        entity = get_by_short_code(dbm, case_insensitive_lookup(form_model.entity_question.code, submission.values), [form_model.entity_type[0]])

        return entity.data['name']['value'], entity.short_code
    except DataObjectNotFound:
        return "N/A", "--"

def get_leading_part(dbm, form_model, submissions, user):
    result = []

    rp_field = form_model.event_time_question

    is_first_element_needed = form_model.entity_type != ['reporter']
    for submission in submissions:
        data_sender = get_data_sender(dbm, user, submission)
        submission_date = _to_str(submission.created)
        row = [submission_date, data_sender]
        if rp_field:
            reporting_period = case_insensitive_lookup(rp_field.code, submission.values) if rp_field else None
            reporting_period = _to_str(reporting_period, rp_field)
            row = [reporting_period] + row

        if is_first_element_needed:
            first_element = get_first_element_of_leading_part(dbm, form_model, submission, data_sender)
            row = [first_element] + row

        result.append(row)

    return result

def _to_str(value, form_field=None):
    if value is None:
        return u"--"
    if is_sequence(value):
        return sequence_to_str(value)
    if isinstance(value, datetime):
        date_format = DateField.FORMAT_DATE_DICTIONARY.get(form_field.date_format) if form_field else 'dd.MM.yyyy'
        return format_date(value, date_format)
    return value


def _to_value_list_headers(first_element, header_list, value_dict):
    return [first_element] + [_to_str(value_dict.get(header)) for header in header_list[1:]]


def _to_value_list(first_element, form_model, value_dict):
    form_fields = form_model.fields

    return [first_element] + [_to_str(value_dict.get(field.label[form_model.activeLanguages[0]]), field) for field in
                              form_fields[1:]]

def to_value_list_based_on_field_order(fields, value_dict):
    return [_to_str(value_dict.get(field.code, field)) for field in fields]


def get_all_values(data_dictionary, form_model):
    """
       data_dictionary = {'Clinic/cid002': {'What is age of father?': 55, 'What is your name?': 'shweta', 'What is associated entity?': 'cid002'}, 'Clinic/cid001': {'What is age of father?': 35, 'What is your name?': 'asif', 'What is associated entity?': 'cid001'}}
       header_list = ["What is associated entity", "What is your name", "What is age of father?"]
       expected_list = [ ['cid002',''shweta', 55 ],['cid001','asif', 35]]
    """
    header_list = get_headers(form_model)
    entity_question_description = form_model.entity_question.name
    grand_totals_dict = data_dictionary.pop('GrandTotals') if 'GrandTotals' in data_dictionary else {}
    grand_totals = _to_value_list_headers("Grand Total", header_list, grand_totals_dict)
    return [_to_value_list(value_dict.get(entity_question_description), form_model, value_dict) for value_dict in
            data_dictionary.values()], grand_totals


def replace_options_with_real_answer(form_model, answer):
    return {field.code: get_according_value(answer, field) for field in form_model.fields}


def format_submission_values(form_model, values):
    field_without_rp = [field for field in form_model.fields if not field.is_event_time_field]
    field_values = []
    for idx, value in enumerate(values):
        values[idx] = replace_options_with_real_answer(form_model, value)
        ordered_answers = to_value_list_based_on_field_order(field_without_rp, values[idx])
        field_values.append(ordered_answers)
    return field_values


def format_answer_for_presentation(form_model, submissions):
    values = [submission.values for submission in submissions]
    return format_submission_values(form_model, values)




def to_lowercase_submission_keys(submissions):
    for submission in submissions:
        values = submission.values
        submission._doc.values = dict((k.lower(), v) for k,v in values.iteritems())


def filter_submissions(filters, form_model, manager):
    assert isinstance(form_model, FormModel)
    submissions = get_submissions(manager, form_model.form_code, None, None, view_name=SUCCESS_SUBMISSION_LOG_VIEW_NAME)
    to_lowercase_submission_keys(submissions)
    for filter in filters:
        submissions = filter.filter(submissions)
    return submissions


def get_leading_and_field_values(filters, form_model, manager, request):
    submissions = filter_submissions(filters, form_model, manager)

    leading_part_answer = get_leading_part(manager, form_model, submissions, request.user)

    values = [submission.values for submission in submissions]
    field_values = format_submission_values(form_model, values)
    return leading_part_answer, field_values


def get_field_values(request, manager, form_model, filters=[]):
    leading_part_answer, field_values = get_leading_and_field_values(filters, form_model, manager, request)
    return [leading + remaining[1:] for leading, remaining in zip(leading_part_answer, field_values)]

def get_formatted_time_string(time_val):
    try:
        time_val = datetime.strptime(time_val, '%d-%m-%Y %H:%M:%S')
    except Exception:
        return None
    return time_val.strftime('%d-%m-%Y %H:%M:%S')


def remove_reporter(entity_type_list):
    removable = None
    for each in entity_type_list:
        if each[0].lower() == 'reporter':
            removable = each
    entity_type_list.remove(removable)
    entity_type_list.sort()
    return entity_type_list


def get_preview_for_field(field):
    preview =  {"description": field.name, "code": field.code, "type": field.type, "instruction": field.instruction}
    constraints = field.get_constraint_text() if field.type not in ["select", "select1"] else \
        [(option["text"][field.language], option["val"]) for option in field.options]
    preview.update({"constraints": constraints})
    return preview

def delete_project(manager, project, void=True):
    project_id, qid = project.id, project.qid
    [reminder.void(void) for reminder in (Reminder.objects.filter(project_id=project_id))]
    questionnaire = FormModel.get(manager, qid)
    [submission.void(void) for submission in get_submissions(manager, questionnaire.form_code, None, None)]
    questionnaire.void(void)
    project.set_void(manager, void)


def get_activity_report_questions(dbm):
    reporting_period_dict_type = get_or_create_data_dict(dbm=dbm, name="rpd", slug="reporting_period",
        primitive_type="date",
        description="activity reporting period")
    activity_report_question = DateField(name=ugettext("What is the reporting period for the activity?"), code='q1',
        label="Period being reported on", ddtype=reporting_period_dict_type,
        date_format="dd.mm.yyyy", event_time_field_flag=True)

    return [activity_report_question]


def get_subject_report_questions(dbm):
    entity_id_question = _create_entity_id_question(dbm, 'q1')
    reporting_period_dict_type = get_or_create_data_dict(dbm=dbm, name="rpd", slug="reporting_period",
        primitive_type="date",
        description="activity reporting period")
    activity_report_question = DateField(name=ugettext("What is the reporting period for the activity?"), code='q2',
        label="Period being reported on", ddtype=reporting_period_dict_type,
        date_format="dd.mm.yyyy", event_time_field_flag=True)
    return [entity_id_question, activity_report_question]


def broadcast_message(data_senders, message, organization_tel_number, other_numbers, message_tracker):
    sms_client = SMSClient()
    sms_sent = None
    for data_sender in data_senders:
        phone_number = data_sender.get(
            'mobile_number') #This should not be a dictionary but the API in import_data should be fixed to return entity
        if phone_number is not None:
            logger.info(("Sending broadcast message to %s from %s") % (phone_number, organization_tel_number))
            sms_sent = sms_client.send_sms(organization_tel_number, phone_number, message)
        if sms_sent:
            message_tracker.increment_outgoing_message_count_by(1)

    for number in other_numbers:
        number = number.strip()
        logger.info(("Sending broadcast message to %s from %s") % (number, organization_tel_number))
        sms_sent = sms_client.send_sms(organization_tel_number, number, message)
        if sms_sent:
            message_tracker.increment_outgoing_message_count_by(1)

    return sms_sent


def create_request(questionnaire_form, username, is_update=None):
    return Request(message=questionnaire_form.cleaned_data,
        transportInfo=
        TransportInfo(transport="web",
            source=username,
            destination=""
        ), is_update=is_update)


def _translate_messages(error_dict, fields):
    errors = dict()

    for field in fields:
        if field.code in error_dict:
            error = error_dict[field.code][0]
            if type(field) == TextField:
                text, code = error.split(' ')[1], field.code
                errors[code] = [_("Answer %s for question %s is longer than allowed.") % (text, code)]
            if type(field) == IntegerField:
                number, error_context = error.split(' ')[1], error.split(' ')[6]
                errors[field.code] = [
                    _("Answer %s for question %s is %s than allowed.") % (number, field.code, _(error_context),)]
            if type(field) == GeoCodeField:
                errors[field.code] = [_(
                    "Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315")]
            if type(field) == DateField:
                answer, format = error.split(' ')[1], field.date_format
                errors[field.code] = [_("Answer %s for question %s is invalid. Expected date in %s format") % (
                    answer, field.code, format)]

    return errors


def errors_to_list(errors, fields):
    error_dict = dict()
    for key, value in errors.items():
        error_dict.update({key: [value] if not isinstance(value, list) else value})
    return _translate_messages(error_dict, fields)


