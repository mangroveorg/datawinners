# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from mangrove.datastore.database import get_db_manager
from mangrove.datastore.datadict import create_datadict_type, get_datadict_type_by_slug
from mangrove.errors.MangroveException import DataObjectNotFound
from mangrove.form_model.field import TextField, IntegerField, SelectField, DateField
from mangrove.form_model.form_model import FormModel
from mangrove.form_model.validation import NumericConstraint, TextConstraint
from mangrove.utils.helpers import slugify
from mangrove.utils.types import is_empty, is_sequence, is_not_empty
import models


def get_or_create_data_dict(dbm, name, slug, primitive_type, description=None):
    try:
        #  Check if is existing
        ddtype = get_datadict_type_by_slug(dbm, slug)
    except DataObjectNotFound:
        #  Create new one
        ddtype = create_datadict_type(dbm=dbm, name=name, slug=slug,
                               primitive_type=primitive_type, description=description)
    return ddtype


def create_question(post_dict, dbm=None):
    if dbm is None:
        dbm = get_db_manager()

    options = post_dict.get('options')
    datadict_type = options.get('ddtype') if options is not None else None
    if is_not_empty(datadict_type):
        #  question already has a data dict type
        datadict_slug = datadict_type.get('slug')
    else:
        datadict_slug = str(slugify(unicode(post_dict.get('title'))))
    ddtype = get_or_create_data_dict(dbm=dbm, name=post_dict.get('question_code'), slug=datadict_slug,
                               primitive_type=post_dict.get('type'), description=post_dict.get('title'))

    if post_dict["type"] == "text":
        return _create_text_question(post_dict, ddtype)
    if post_dict["type"] == "integer":
        return _create_integer_question(post_dict, ddtype)
    if post_dict["type"] == "select":
        return _create_select_question(post_dict, single_select_flag=False, ddtype=ddtype)
    if post_dict["type"] == "date":
        return _create_date_question(post_dict, ddtype)
    if post_dict["type"] == "select1":
        return _create_select_question(post_dict, single_select_flag=True, ddtype=ddtype)


def create_questionnaire(post, dbm=get_db_manager()):
    entity_data_dict_type = get_or_create_data_dict(dbm=dbm, name="eid", slug="entity_id", primitive_type="string", description="Entity ID")
    entity_id_question = TextField(name="What are you reporting on?", question_code="eid", label="Entity being reported on",
                                   entity_question_flag=True, ddtype=entity_data_dict_type, length=TextConstraint(min=1, max=12))
    return FormModel(dbm, entity_type=post["entity_type"], name=post["name"], fields=[entity_id_question],
                     form_code=generate_questionnaire_code(dbm), type='survey')


def load_questionnaire(questionnaire_id):
    return get_db_manager().get(questionnaire_id, FormModel)


def update_questionnaire_with_questions(form_model, question_set):
    form_model.delete_all_fields()
    for question in question_set:
        form_model.add_field(create_question(question))
    return form_model


def get_code_and_title(fields):
    return [(each_field.question_code, each_field.name)for each_field in fields]


def _create_text_question(post_dict, ddtype):
    max_length_from_post = post_dict.get("max_length")
    min_length_from_post = post_dict.get("min_length")
    max_length = max_length_from_post if not is_empty(max_length_from_post) else None
    min_length = min_length_from_post if not is_empty(min_length_from_post) else None
    length = TextConstraint(min=min_length, max=max_length)
    return TextField(name=post_dict["title"], question_code=post_dict["question_code"].strip(), label="default",
                     entity_question_flag=post_dict.get("is_entity_question"), length=length, ddtype=ddtype)


def _create_integer_question(post_dict, ddtype):
    max_range_from_post = post_dict["range_max"]
    max_range = max_range_from_post if not is_empty(max_range_from_post) else None
    range = NumericConstraint(min=post_dict["range_min"], max=max_range)
    return IntegerField(name=post_dict["title"], question_code=post_dict["question_code"].strip(), label="default", range=range, ddtype=ddtype)


def _create_date_question(post_dict, ddtype):
    return DateField(name=post_dict["title"], question_code=post_dict["question_code"].strip(), label="default", date_format=post_dict.get('date_format'), ddtype=ddtype)


def _create_select_question(post_dict, single_select_flag, ddtype):
    options = [choice.get("text") for choice in post_dict["choices"]]
    return SelectField(name=post_dict["title"], question_code=post_dict["question_code"].strip(), label="default",
                       options=options, single_select_flag=single_select_flag, ddtype=ddtype)


def get_submissions(questions, submissions):
    assert is_sequence(questions)
    assert is_sequence(submissions)
    for s in submissions:
        assert isinstance(s, dict) and s.get('values') is not None
    formatted_list = [[each.get('created'), each.get('channel'), each.get('status'), each.get('error_message')] + [each.get('values').get(q[0]) for q in questions] for each in submissions]
    return [tuple(each) for each in formatted_list]


def generate_questionnaire_code(dbm):
    all_projects = models.get_all_projects(dbm)
    code = len(all_projects) + 1
    return "%03d" % (code,)

