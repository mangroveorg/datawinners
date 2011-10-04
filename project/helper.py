# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datawinners.entity.import_data import load_all_subjects_of_type
from mangrove.datastore.datadict import create_datadict_type, get_datadict_type_by_slug
from mangrove.datastore.documents import attributes
from mangrove.errors.MangroveException import DataObjectNotFound, FormModelDoesNotExistsException
from mangrove.form_model.field import TextField, IntegerField, SelectField, DateField, GeoCodeField
from mangrove.form_model.form_model import FormModel, get_form_model_by_code, REPORTER
from mangrove.form_model.validation import NumericRangeConstraint, TextLengthConstraint
from mangrove.utils.helpers import slugify
from mangrove.utils.types import is_empty, is_sequence, is_not_empty, is_string, sequence_to_str
from mangrove.datastore import aggregrate as aggregate_module
from django.utils.translation import  ugettext
import models
import xlwt
from datetime import datetime
from mangrove.transport.submissions import ENTITY_QUESTION_DISPLAY_CODE, Submission, get_submissions
from models import Reminder

NUMBER_TYPE_OPTIONS = ["Latest", "Sum", "Count", "Min", "Max", "Average"]
MULTI_CHOICE_TYPE_OPTIONS = ["Latest"]
DATE_TYPE_OPTIONS = ["Latest"]
GEO_TYPE_OPTIONS = ["Latest"]
TEXT_TYPE_OPTIONS = ["Latest"]
TEST_FLAG = 'TEST'


def get_or_create_data_dict(dbm, name, slug, primitive_type, description=None):
    try:
        #  Check if is existing
        ddtype = get_datadict_type_by_slug(dbm, slug)
    except DataObjectNotFound:
        #  Create new one
        ddtype = create_datadict_type(dbm=dbm, name=name, slug=slug,
                                      primitive_type=primitive_type, description=description)
    return ddtype


def create_question(post_dict, dbm):
    options = post_dict.get('options')
    datadict_type = options.get('ddtype') if options is not None else None
    if is_not_empty(datadict_type):
        #  question already has a data dict type
        datadict_slug = datadict_type.get('slug')
    else:
        datadict_slug = str(slugify(unicode(post_dict.get('title'))))
    ddtype = get_or_create_data_dict(dbm=dbm, name=post_dict.get('code'), slug=datadict_slug,
                                     primitive_type=post_dict.get('type'), description=post_dict.get('title'))

    if post_dict["type"] == "text":
        return _create_text_question(post_dict, ddtype)
    if post_dict["type"] == "integer":
        return _create_integer_question(post_dict, ddtype)
    if post_dict["type"] == "geocode":
        return _create_geo_code_question(post_dict, ddtype)
    if post_dict["type"] == "select":
        return _create_select_question(post_dict, single_select_flag=False, ddtype=ddtype)
    if post_dict["type"] == "date":
        return _create_date_question(post_dict, ddtype)
    if post_dict["type"] == "select1":
        return _create_select_question(post_dict, single_select_flag=True, ddtype=ddtype)


def create_entity_id_question(dbm):
    entity_data_dict_type = get_or_create_data_dict(dbm=dbm, name="eid", slug="entity_id", primitive_type="string",
                                                    description="Entity ID")
    name = "Which subject are you reporting on?"
    entity_id_question = TextField(name=name, code="q1",
                                   label="Entity being reported on",
                                   entity_question_flag=True, ddtype=entity_data_dict_type,
                                   constraints=[TextLengthConstraint(min=1, max=12)])
    return entity_id_question


def create_questionnaire(post, dbm):
    reporting_period_dict_type = get_or_create_data_dict(dbm=dbm, name="rpd", slug="reporting_period",
                                                         primitive_type="date",
                                                         description="activity reporting period")
    entity_type = [post["entity_type"]] if is_string(post["entity_type"]) else post["entity_type"]
    entity_id_question = create_entity_id_question(dbm)
    activity_report_question = DateField(name=ugettext("What is the reporting period for the activity?"), code="q2",
                                         label="Period being reported on", ddtype=reporting_period_dict_type,
                                         date_format="dd.mm.yyyy")
    fields = [entity_id_question, activity_report_question]
    return FormModel(dbm, entity_type=entity_type, name=post["name"], fields=fields,
                     form_code=generate_questionnaire_code(dbm), type='survey', state=attributes.INACTIVE_STATE, language=post['language'])

def update_questionnaire_with_questions(form_model, question_set, dbm):
    form_model.delete_all_fields()
    for question in question_set:
        form_model.add_field(create_question(question, dbm))
    return form_model

def _create_text_question(post_dict, ddtype):
    max_length_from_post = post_dict.get("max_length")
    min_length_from_post = post_dict.get("min_length")
    max_length = max_length_from_post if not is_empty(max_length_from_post) else None
    min_length = min_length_from_post if not is_empty(min_length_from_post) else None
    constraints = []
    if not (max_length is None and min_length is None):
        constraints.append(TextLengthConstraint(min=min_length, max=max_length))
    return TextField(name=post_dict["title"], code=post_dict["code"].strip(), label="default",
                     entity_question_flag=post_dict.get("is_entity_question"), constraints=constraints, ddtype=ddtype,
                     instruction=post_dict.get("instruction"))


def _create_integer_question(post_dict, ddtype):
    max_range_from_post = post_dict.get("range_max")
    min_range_from_post = post_dict.get("range_min")
    max_range = max_range_from_post if not is_empty(max_range_from_post) else None
    min_range = min_range_from_post if not is_empty(min_range_from_post) else None
    range = NumericRangeConstraint(min=min_range, max=max_range)
    return IntegerField(name=post_dict["title"], code=post_dict["code"].strip(), label="default",
                        constraints=[range], ddtype=ddtype, instruction=post_dict.get("instruction"))


def _create_date_question(post_dict, ddtype):
    return DateField(name=post_dict["title"], code=post_dict["code"].strip(), label="default",
                     date_format=post_dict.get('date_format'), ddtype=ddtype, instruction=post_dict.get("instruction"))


def _create_geo_code_question(post_dict, ddtype):
    return GeoCodeField(name=post_dict["title"], code=post_dict["code"].strip(), label="default", ddtype=ddtype,
                        instruction=post_dict.get("instruction"))


def _create_select_question(post_dict, single_select_flag, ddtype):
    options = [(choice.get("text"), choice.get("val")) for choice in post_dict["choices"]]
    return SelectField(name=post_dict["title"], code=post_dict["code"].strip(), label="default",
                       options=options, single_select_flag=single_select_flag, ddtype=ddtype,
                       instruction=post_dict.get("instruction"))


def adapt_submissions_for_template(questions, submissions):
    assert is_sequence(questions)
    assert is_sequence(submissions)
    for s in submissions:
        assert type(s) is Submission and s._doc is not None
    formatted_list = []
    for each in submissions:
        formatted_list.append(
            [each.uuid, each.destination, each.source, each.created, each.errors, each.status]+
            [each.data_record.is_void() if each.data_record is not None else True] + [each.values.get(q.code.lower()) for q in questions])

    return [tuple(each) for each in formatted_list]


def generate_questionnaire_code(dbm):
    all_projects = models.get_all_projects(dbm)
    code = len(all_projects) + 1
    code = "%03d" % (code,)
    while True:
        try:
            get_form_model_by_code(dbm, code)
            code = int(code) + 1
            code = "%03d" % (code,)
        except FormModelDoesNotExistsException:
            break
    return code


def get_aggregation_options_for_all_fields(fields):
    type_dictionary = dict(IntegerField=NUMBER_TYPE_OPTIONS, TextField=TEXT_TYPE_OPTIONS, DateField=DATE_TYPE_OPTIONS,
                           GeoCodeField=GEO_TYPE_OPTIONS, SelectField=MULTI_CHOICE_TYPE_OPTIONS)
    type_list = []
    for field in fields:
        field_type = field.__class__.__name__
        #TODO- Future functionality. Removing for beta-release. Uncomment this when aggregations for multiple choice field are added.
        #        if field_type == "SelectField":
        #            choice_type = copy(MULTI_CHOICE_TYPE_OPTIONS)
        #            choice_type.extend(["sum(" + choice.get("text").get(field.language) + ")"for choice in
        #                                field.options])
        #            choice_type.extend(["percent(" + choice.get("text").get(field.language) + ")" for choice in
        #                                field.options])
        #            type_list.append(choice_type)
        #        else:
        type_list.append(type_dictionary.get(field_type))
    return type_list


def get_headers(form_model):
    return [form_model.entity_type[0] + " Code"] + [field.name for field in form_model.fields[1:]]


def _to_str(value):
    if value is None:
        return u"--"
    if is_sequence(value):
        return sequence_to_str(value)
    return value


def _to_value_list(first_element, header_list, value_dict):
    return [first_element] + [_to_str(value_dict.get(header)) for header in header_list[1:]]


def get_all_values(data_dictionary, header_list, entity_question_description):
    """
       data_dictionary = {'Clinic/cid002': {'What is age of father?': 55, 'What is your name?': 'shweta', 'What is associated entity?': 'cid002'}, 'Clinic/cid001': {'What is age of father?': 35, 'What is your name?': 'asif', 'What is associated entity?': 'cid001'}}
       header_list = ["What is associated entity", "What is your name", "What is age of father?"]
       expected_list = [ ['cid002',''shweta', 55 ],['cid001','asif', 35]]
    """
    grand_totals_dict = data_dictionary.pop('GrandTotals') if 'GrandTotals' in data_dictionary else {}
    grand_totals = _to_value_list("Grand Total", header_list, grand_totals_dict)
    return [_to_value_list(value_dict.get(entity_question_description), header_list, value_dict) for value_dict in data_dictionary.values()], grand_totals


def get_aggregate_dictionary(header_list, post_data):
    aggregates = {}
    #    my_dictionary =
    for index, key in enumerate(header_list):
        aggregates[key] = post_data[index].strip().lower()
    return aggregates


def get_aggregate_list(fields, post_data):
    aggregates = []
    for index, field in enumerate(fields):
        aggregates.append(aggregate_module.aggregation_factory(post_data[index].strip().lower(), field.name))
    return aggregates


def get_formatted_time_string(time_val):
    try:
        time_val = datetime.strptime(time_val, '%d-%m-%Y %H:%M:%S')
    except Exception:
        return None
    return time_val.strftime('%d-%m-%Y %H:%M:%S')


def get_excel_sheet(raw_data, sheet_name):
    wb = xlwt.Workbook()
    ws = wb.add_sheet(sheet_name)
    for row_number, row  in enumerate(raw_data):
        for col_number, val in enumerate(row):
            ws.write(row_number, col_number, val)
    return wb


def remove_reporter(entity_type_list):
    removable = None
    for each in entity_type_list:
        if each[0].lower() == 'reporter':
            removable = each
    entity_type_list.remove(removable)
    entity_type_list.sort()
    return entity_type_list


def get_preview_for_field(field):
    return {"description": field.name, "code": field.code, "type": field.type,
            "constraints": field.get_constraint_text(), "instruction": field.instruction}


def _add_to_dict(dict, post_dict,key):
    if post_dict.get(key):
        dict[key] = post_dict.get(key)


def deadline_and_reminder(post_dict):
    dict={}
    _add_to_dict(dict, post_dict,'frequency_enabled')
    _add_to_dict(dict, post_dict,'frequency_period')
    _add_to_dict(dict, post_dict,'has_deadline')
    _add_to_dict(dict, post_dict,'deadline_week')
    _add_to_dict(dict, post_dict,'deadline_month')
    _add_to_dict(dict, post_dict,'deadline_type')
    _add_to_dict(dict, post_dict,'reminders_enabled')
    return dict

def get_project_data_senders(manager, project):
    all_data = load_all_subjects_of_type(manager)
    return [data for data in all_data if data['short_name'] in project.data_senders]

def delete_project(manager, project, void = True):
    project_id, qid = project.id, project.qid
    [reminder.void(void) for reminder in (Reminder.objects.filter(project_id=project_id))]
    questionnaire = FormModel.get(manager, qid)
    [submission.void(void) for submission in get_submissions(manager, questionnaire.form_code, None, None)]
    questionnaire.void(void)
    project.set_void(manager, void)