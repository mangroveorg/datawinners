# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from mangrove.datastore.datadict import get_datadict_type_by_slug, \
    create_datadict_type
from mangrove.form_model.field import TextField, HierarchyField, GeoCodeField, TelephoneNumberField, IntegerField, DateField, SelectField
from mangrove.form_model.form_model import FormModel
from mangrove.form_model.validation import TextLengthConstraint, \
    RegexConstraint, NumericRangeConstraint
from mangrove.utils.helpers import slugify
from mangrove.utils.types import is_empty, is_not_empty
import re
from mangrove.errors.MangroveException import NumberNotRegisteredException, \
    DataObjectNotFound
from mangrove.transport.reporter import find_reporter_entity
from django.utils.encoding import smart_unicode

REGISTRATION_FORM_CODE = "reg"
ENTITY_TYPE_FIELD_CODE = "t"
ENTITY_TYPE_FIELD_NAME = "entity_type"
LOCATION_TYPE_FIELD_NAME = "location"
LOCATION_TYPE_FIELD_CODE = "l"
GEO_CODE = "g"
GEO_CODE_FIELD = "geo_code"
NAME_FIELD = "name"
NAME_FIELD_CODE = "n"
FIRSTNAME_FIELD = "firstname"
FIRSTNAME_FIELD_CODE = "f"
SHORT_CODE_FIELD = "short_code"
SHORT_CODE = "s"
DESCRIPTION_FIELD = "description"
DESCRIPTION_FIELD_CODE = "d"
MOBILE_NUMBER_FIELD = "mobile_number"
MOBILE_NUMBER_FIELD_CODE = "m"
REPORTER = "reporter"
REPORTER_FORM_CODE = "rep"

def remove_hyphens(telephone_number):
    return re.sub('[- \(\)+]', '', smart_unicode(telephone_number))

def unique(dbm, telephone_number):
    telephone_number = remove_hyphens(telephone_number)
    try:
        find_reporter_entity(dbm, telephone_number)
    except NumberNotRegisteredException:
        return True
    return False


def _get_or_create_data_dict(dbm, name, slug, primitive_type, description=None):
    try:
        ddtype = get_datadict_type_by_slug(dbm, slug)
    except DataObjectNotFound:
        ddtype = create_datadict_type(dbm=dbm, name=name, slug=slug,
                                      primitive_type=primitive_type, description=description)
    return ddtype


def _create_constraints_for_mobile_number():
    mobile_number_length = TextLengthConstraint(max=15)
    mobile_number_pattern = RegexConstraint(reg='^[0-9]+$')
    mobile_constraints = [mobile_number_length, mobile_number_pattern]
    return mobile_constraints


def _generate_form_code(manager, prefix, rank=''):
    form_code = "%s%s" % (prefix, rank)
    rows = manager.load_all_rows_in_view("questionnaire", key=form_code)
    if len(rows) > 0:
        rank = 1 if rank is None else rank + 1
        form_code = _generate_form_code(manager, prefix, rank)
    return form_code


def _create_registration_form(manager, entity_name=None, form_code=None, entity_type=None):
    location_type = _get_or_create_data_dict(manager, name='Location Type', slug='location', primitive_type='string')
    geo_code_type = _get_or_create_data_dict(manager, name='GeoCode Type', slug='geo_code', primitive_type='geocode')
    name_type = _get_or_create_data_dict(manager, name='Name', slug='name', primitive_type='string')
    mobile_number_type = _get_or_create_data_dict(manager, name='Mobile Number Type', slug='mobile_number', primitive_type='string')

    question1 = TextField(name=FIRSTNAME_FIELD, code=FIRSTNAME_FIELD_CODE, label="What is the %s's first name?" % (entity_name,),
                          defaultValue="some default value", language="en", ddtype=name_type,
                          instruction="Enter a %s first name" % (entity_name,))
    question2 = TextField(name=NAME_FIELD, code=NAME_FIELD_CODE, label="What is the %s's last name?" % (entity_name,),
                              defaultValue="some default value", language="en", ddtype=name_type,
                              instruction="Enter a %s last name" % (entity_name,))
    question3 = TextField(name=SHORT_CODE_FIELD, code=SHORT_CODE, label="What is the %s's Unique ID Number" % (entity_name,),
                          defaultValue="some default value", language="en", ddtype=name_type,
                          instruction="Enter an id, or allow us to generate it",
                          entity_question_flag=True,
                          constraints=[TextLengthConstraint(max=12)], required=False)
    question4 = HierarchyField(name=LOCATION_TYPE_FIELD_NAME, code=LOCATION_TYPE_FIELD_CODE,
                               label="What is the %s's location?" % (entity_name,),
                               language="en", ddtype=location_type, instruction="Enter a region, district, or commune",
                               required=False)
    question5 = GeoCodeField(name=GEO_CODE_FIELD, code=GEO_CODE, label="What is the %s's GPS co-ordinates?" % (entity_name,),
                             language="en", ddtype=geo_code_type,
                             instruction="Enter lat and long. Eg 20.6, 47.3", required=False)
    question6 = TelephoneNumberField(name=MOBILE_NUMBER_FIELD, code=MOBILE_NUMBER_FIELD_CODE,
                                     label="What is the %s's mobile telephone number?" % (entity_name,),
                                     defaultValue="some default value", language="en", ddtype=mobile_number_type,
                                     instruction="Enter the %s's number" % (entity_name,), constraints=(
                                     _create_constraints_for_mobile_number()), required=False)
    questions = [question1, question2, question3, question4, question5, question6]

    form_model = FormModel(manager, name=entity_name, form_code=form_code, fields=questions , is_registration_model=True, entity_type=entity_type)
    return form_model


def create_registration_form(manager, entity_name):
    prefix = entity_name.lower()[:3]
    form_code = _generate_form_code(manager, prefix)
    form_model = _create_registration_form(manager, entity_name, form_code, [entity_name])
    form_model.save()


def create_question(post_dict, dbm):
    options = post_dict.get('options')
    datadict_type = options.get('ddtype') if options is not None else None
    if is_not_empty(datadict_type):
        datadict_slug = datadict_type.get('slug')
    else:
        datadict_slug = str(slugify(unicode(post_dict.get('title'))))
    ddtype = _get_or_create_data_dict(dbm=dbm, name=post_dict.get('code'), slug=datadict_slug,
                                     primitive_type=post_dict.get('type'), description=post_dict.get('title'))

    if "name" not in post_dict:
        post_dict["name"] = post_dict["code"]

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
    if post_dict["type"] == "telephone_number":
        return _create_telephone_number_question(post_dict, ddtype)
    if post_dict["type"] == "list":
        return _create_location_question(post_dict, ddtype)

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
    return TextField(name=post_dict["name"], code=post_dict["code"].strip(), label=post_dict["title"],
                     entity_question_flag=post_dict.get("is_entity_question"), constraints=constraints, ddtype=ddtype,
                     instruction=post_dict.get("instruction"),required=post_dict.get("required"))


def _create_integer_question(post_dict, ddtype):
    max_range_from_post = post_dict.get("range_max")
    min_range_from_post = post_dict.get("range_min")
    max_range = max_range_from_post if not is_empty(max_range_from_post) else None
    min_range = min_range_from_post if not is_empty(min_range_from_post) else None
    range = NumericRangeConstraint(min=min_range, max=max_range)
    return IntegerField(name=post_dict["name"], code=post_dict["code"].strip(), label=post_dict["title"],
                        constraints=[range], ddtype=ddtype, instruction=post_dict.get("instruction"),
                        required=post_dict.get("required"))


def _create_date_question(post_dict, ddtype):
    return DateField(name=post_dict["name"], code=post_dict["code"].strip(), label=post_dict["title"],
                     date_format=post_dict.get('date_format'), ddtype=ddtype, instruction=post_dict.get("instruction"),required=post_dict.get("required"), event_time_field_flag=post_dict.get('event_time_field_flag', False))


def _create_geo_code_question(post_dict, ddtype):
    return GeoCodeField(name=post_dict["name"], code=post_dict["code"].strip(), label=post_dict["title"], ddtype=ddtype,
                        instruction=post_dict.get("instruction"),required=post_dict.get("required"))


def _create_select_question(post_dict, single_select_flag, ddtype):
    options = [(choice.get("text"), choice.get("val")) for choice in post_dict["choices"]]
    return SelectField(name=post_dict["name"], code=post_dict["code"].strip(), label=post_dict["title"],
                       options=options, single_select_flag=single_select_flag, ddtype=ddtype,
                       instruction=post_dict.get("instruction"),required=post_dict.get("required"))

def _create_telephone_number_question(post_dict, ddtype):
    return TelephoneNumberField(name=post_dict["name"], code=post_dict["code"].strip(),
                                     label=post_dict["title"], ddtype=ddtype,
                                     instruction=post_dict.get("instruction"), constraints=(
            _create_constraints_for_mobile_number()),required=post_dict.get("required"))


def _create_location_question(post_dict, ddtype):
    return HierarchyField(name=post_dict["name"], code=post_dict["code"].strip(),
                               label=post_dict["title"], ddtype=ddtype, instruction=post_dict.get("instruction"),
                               required=post_dict.get("required"))