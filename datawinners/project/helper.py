# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import logging
from babel.dates import format_date
from django.http import Http404
from django.utils.translation import gettext as _
from django.utils.translation import ugettext
from datawinners.accountmanagement.models import NGOUserProfile
from datawinners.scheduler.smsclient import SMSClient
from mangrove.datastore.datadict import create_datadict_type, get_datadict_type_by_slug
from mangrove.errors.MangroveException import DataObjectNotFound, FormModelDoesNotExistsException
from mangrove.form_model.field import TextField, IntegerField, DateField, GeoCodeField
from mangrove.form_model.form_model import FormModel, get_form_model_by_code
from mangrove.form_model.validation import  TextLengthConstraint
from mangrove.utils.types import  is_sequence, sequence_to_str
import models
from datetime import datetime
from models import Reminder
from mangrove.transport.contract.submission import Submission
from mangrove.transport.repository.survey_responses import get_survey_responses
from mangrove.transport.contract.transport_info import TransportInfo
from mangrove.transport.contract.request import Request

SUBMISSION_DATE_FORMAT_FOR_SUBMISSION = "%b. %d, %Y, %I:%M %p"

DEFAULT_DATE_FORMAT = 'dd.MM.yyyy'

NOT_AVAILABLE = "N/A"
NOT_AVAILABLE_DS = "Unknown"

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
        constraints=[TextLengthConstraint(min=1, max=20)],
        instruction=(ugettext('Answer must be a word %d characters maximum') % 20))
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
            [each.uuid, each.destination, each.owner_uid, each.created, each.errors,
             "Success" if each.status else "Error"] +
            ["Yes" if is_submission_deleted(each.data_record) else "No"] + [
            get_according_value(case_insensitive_dict, q) for q in questions])

    return [tuple(each) for each in formatted_list]


def get_according_value(value_dict, question):
    value = value_dict.get(question.code.lower(), '--')
    if value != '--' and question.type in ['select1', 'select']:
        value_list = question.get_option_value_list(value)
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

def get_org_id_by_user(user):
    return NGOUserProfile.objects.get(user=user).org_id

def case_insensitive_lookup(search_key, dictionary):
    assert isinstance(dictionary, dict)
    for key, value in dictionary.items():
        if key.lower() == search_key.lower():
            return value
    return None

def get_values_from_dict(dictionary):
    for key, value in dictionary.items():
        return value

def _to_str(value, form_field=None):
    if value is None:
        return u"--"
    if is_sequence(value):
        return sequence_to_str(value)
    if isinstance(value, datetime):
        date_format = DateField.FORMAT_DATE_DICTIONARY.get(
            form_field.date_format) if form_field else DEFAULT_DATE_FORMAT
        return format_date(value, date_format)
    return value

def format_dt_for_submission_log_page(survey_response):
    return survey_response.submitted_on.strftime(SUBMISSION_DATE_FORMAT_FOR_SUBMISSION)

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
    preview = {"description": field.name, "code": field.code, "type": field.type, "instruction": field.instruction}
    constraints = field.get_constraint_text() if field.type not in ["select", "select1"] else\
    [(option["text"], option["val"]) for option in field.options]
    preview.update({"constraints": constraints})
    return preview

def delete_project(manager, project, void=True):
    project_id, qid = project.id, project.qid
    [reminder.void(void) for reminder in (Reminder.objects.filter(project_id=project_id))]
    questionnaire = FormModel.get(manager, qid)
    [survey_response.void() for survey_response in get_survey_responses(manager, questionnaire.form_code, None, None)]
    questionnaire.void()
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

def broadcast_message(data_senders, message, organization_tel_number, other_numbers, message_tracker, country_code=None):
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
        if country_code:
            number = "%s%s" % (country_code, number[1:])

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
                errors[code] = [ugettext("Answer %s for question %s is longer than allowed.") % (text, code)]
            if type(field) == IntegerField:
                number, error_context = error.split(' ')[1], error.split(' ')[6]
                errors[field.code] = [
                    ugettext("Answer %s for question %s is %s than allowed.") % (number, field.code, _(error_context),)]
            if type(field) == GeoCodeField:
                errors[field.code] = [ugettext(
                    "Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315")]
            if type(field) == DateField:
                answer, format = error.split(' ')[1], field.date_format
                errors[field.code] = [ugettext("Answer %s for question %s is invalid. Expected date in %s format") % (
                    answer, field.code, format)]

    return errors


def errors_to_list(errors, fields):
    error_dict = dict()
    for key, value in errors.items():
        field_index = int(key[1:]) -1
        error_dict.update({fields[field_index].code: [value] if not isinstance(value, list) else value})
    return _translate_messages(error_dict, fields)


def is_project_exist(f):
    def wrapper(*args, **kw):
        try:
            ret = f(*args, **kw)
        except AttributeError, e:
            if e[0] == "'NoneType' object has no attribute 'qid'":
                raise Http404
            raise e
        return ret

    return wrapper