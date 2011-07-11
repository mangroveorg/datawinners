# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from mangrove.datastore.datadict import create_datadict_type, get_datadict_type_by_slug
from mangrove.errors.MangroveException import DataObjectNotFound, FormModelDoesNotExistsException
from mangrove.form_model.field import TextField, IntegerField, SelectField, DateField, GeoCodeField
from mangrove.form_model.form_model import FormModel, get_form_model_by_code, REPORTER
from mangrove.form_model.validation import NumericConstraint, TextConstraint
from mangrove.utils.helpers import slugify
from mangrove.utils.types import is_empty, is_sequence, is_not_empty, is_string
from mangrove.datastore import aggregrate as aggregate_module
import models
import xlwt
from copy import copy
from datetime import datetime
from mangrove.transport.submissions import ENTITY_QUESTION_DISPLAY_CODE

NUMBER_TYPE_OPTIONS = ["Latest", "Sum", "Count", "Min", "Max", "Average"]
MULTI_CHOICE_TYPE_OPTIONS = ["Latest"]
DATE_TYPE_OPTIONS = ["Latest"]
GEO_TYPE_OPTIONS = ["Latest"]
TEXT_TYPE_OPTIONS = ["Latest", "Most Frequent"]


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
    entity_id_question = TextField(name=name, code=ENTITY_QUESTION_DISPLAY_CODE,
                                   label="Entity being reported on",
                                   entity_question_flag=True, ddtype=entity_data_dict_type,
                                   length=TextConstraint(min=1, max=12))
    return entity_id_question


def create_questionnaire(post, dbm):

    reporting_period_dict_type = get_or_create_data_dict(dbm=dbm, name="rpd", slug="reporting_period", primitive_type="date",
                                                    description="activity reporting period")
    entity_type = [post["entity_type"]] if is_string(post["entity_type"]) else post["entity_type"]
    entity_id_question = create_entity_id_question(dbm)
    activity_report_question = DateField(name="What is the reporting period for the activity?", code="rpd", label="Period being reported on", ddtype=reporting_period_dict_type, date_format="dd.mm.yyyy")
    fields = [entity_id_question]
    if entity_type == [REPORTER]:
        fields = [entity_id_question, activity_report_question]
    return FormModel(dbm, entity_type=entity_type, name=post["name"], fields=fields,
                     form_code=generate_questionnaire_code(dbm), type='survey')


def load_questionnaire(dbm, questionnaire_id):
    return dbm.get(questionnaire_id, FormModel)


def update_questionnaire_with_questions(form_model, question_set, dbm):
    form_model.delete_all_fields()
    if form_model.entity_defaults_to_reporter():
        form_model.add_field(create_entity_id_question(dbm))
    for question in question_set:
        form_model.add_field(create_question(question, dbm))
    return form_model


def get_code_and_title(fields):
    return [(each_field.code, each_field.name)for each_field in fields]


def _create_text_question(post_dict, ddtype):
    max_length_from_post = post_dict.get("max_length")
    min_length_from_post = post_dict.get("min_length")
    max_length = max_length_from_post if not is_empty(max_length_from_post) else None
    min_length = min_length_from_post if not is_empty(min_length_from_post) else None
    length = TextConstraint(min=min_length, max=max_length)
    return TextField(name=post_dict["title"], code=post_dict["code"].strip(), label="default",
                     entity_question_flag=post_dict.get("is_entity_question"), length=length, ddtype=ddtype, instruction=post_dict.get("instruction"))


def _create_integer_question(post_dict, ddtype):
    max_range_from_post = post_dict.get("range_max")
    min_range_from_post = post_dict.get("range_min")
    max_range = max_range_from_post if not is_empty(max_range_from_post) else None
    min_range = min_range_from_post if not is_empty(min_range_from_post) else None
    range = NumericConstraint(min=min_range, max=max_range)
    return IntegerField(name=post_dict["title"], code=post_dict["code"].strip(), label="default",
                        range=range, ddtype=ddtype, instruction=post_dict.get("instruction"))


def _create_date_question(post_dict, ddtype):
    return DateField(name=post_dict["title"], code=post_dict["code"].strip(), label="default",
                     date_format=post_dict.get('date_format'), ddtype=ddtype, instruction=post_dict.get("instruction"))


def _create_geo_code_question(post_dict, ddtype):
    return GeoCodeField(name=post_dict["title"], code=post_dict["code"].strip(), label="default", ddtype=ddtype, instruction=post_dict.get("instruction"))


def _create_select_question(post_dict, single_select_flag, ddtype):
    options = [choice.get("text") for choice in post_dict["choices"]]
    return SelectField(name=post_dict["title"], code=post_dict["code"].strip(), label="default",
                       options=options, single_select_flag=single_select_flag, ddtype=ddtype, instruction=post_dict.get("instruction"))


def get_submissions(questions, submissions):
    assert is_sequence(questions)
    assert is_sequence(submissions)
    for s in submissions:
        assert isinstance(s, dict) and s.get('values') is not None
    formatted_list = [
    [each.get('destination'), each.get('source'), each.get('created'), each.get('status'), each.get('voided'), each.get('error_message')] +
    [each.get('values').get(q[0].lower()) for q in questions] for each in submissions]
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


def get_type_list(fields):
    type_dictionary = dict(IntegerField=NUMBER_TYPE_OPTIONS, TextField=TEXT_TYPE_OPTIONS, DateField=DATE_TYPE_OPTIONS,
                           GeoCodeField=GEO_TYPE_OPTIONS)
    type_list = []
    for field in fields:
        field_type = field.__class__.__name__
        if field_type == "SelectField":
            choice_type = copy(MULTI_CHOICE_TYPE_OPTIONS)
            choice_type.extend(["sum(" + choice.get("text").get(field.language) + ")"for choice in
                                field.options])
            choice_type.extend(["percent(" + choice.get("text").get(field.language) + ")" for choice in
                                field.options])
            type_list.append(choice_type)
        else:
            type_list.append(type_dictionary.get(field_type))
    return type_list


def get_headers(field_list):
    assert is_sequence(field_list)
    return [each.name for each in field_list]


def get_values(data_dictionary, header_list):
    """
       data_dictionary = {'Clinic/cid002': {'What is age of father?': 55, 'What is your name?': 'shweta', 'What is associated entity?': 'cid002'}, 'Clinic/cid001': {'What is age of father?': 35, 'What is your name?': 'asif', 'What is associated entity?': 'cid001'}}
       header_list = ["What is associated entity", "What is your name", "What is age of father?"]
       expected_list = [{"entity_name":"cid002", "values":['shweta', 55 ]}, {"entity_name":"cid001", "values":['asif', 35]}]
    """
    value_list = []
    for key, values in data_dictionary.items():
        current_dict = dict()
        current_dict["entity_name"] = values.get(header_list[0])
        current_dict["values"] = list()
        for each in header_list[1:]:
            current_val = values.get(each)
            if type(current_val) == list:
                if type(current_val[0]) != str:
                    current_val = [str(each) for each in current_val]
                current_val = ",".join(current_val)
            current_dict["values"].append(current_val)
        value_list.append(current_dict)
    return value_list


def get_aggregate_dictionary(header_list, post_data):
    aggregates = {}
    #    my_dictionary =
    for index, key in enumerate(header_list):
        aggregates[key] = post_data[index].strip().lower()
    return aggregates


def get_aggregate_list(header_list, post_data):
    aggregates = []
    for index, field_name in enumerate(header_list):
        aggregates.append(aggregate_module.aggregation_factory(post_data[index].strip().lower(), field_name))
    return aggregates


def to_report(data_list):
    """
    data_list = [{"entity_name": "cid002", "values": ['shweta', 55]},
                         {"entity_name": "cid001", "values": ['asif', 35]}]
        expected_list = [["cid002", 'shweta', 55],["cid001", 'asif', 35]]
    """
    final_list = []
    for each in data_list:
        current_list = [each["entity_name"]]
        current_list.extend(each["values"])
        final_list.append(current_list)
    return final_list


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

def hide_entity_question(fields):
    cleaned_fields = [each for each in fields if not each.is_entity_field]
    return cleaned_fields

def remove_reporter(entity_type_list):
    removable = None
    for each in entity_type_list:
        if each[0].lower() == 'reporter':
            removable = each
    entity_type_list.remove(removable)
    entity_type_list.sort()
    return entity_type_list