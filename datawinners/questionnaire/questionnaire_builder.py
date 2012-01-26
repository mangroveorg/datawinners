from django.utils.translation import ugettext
from mangrove.datastore.datadict import create_datadict_type, get_datadict_type_by_slug
from mangrove.errors.MangroveException import DataObjectNotFound
from mangrove.form_model.field import IntegerField, TextField, DateField, SelectField, GeoCodeField
from mangrove.form_model.validation import NumericRangeConstraint, TextLengthConstraint
from mangrove.utils.helpers import slugify
from mangrove.utils.types import is_not_empty, is_empty

class QuestionnaireBuilder(object):
    def __init__(self, form_model, dbm):
        self.form_model = form_model
        self.dbm = dbm

    def update_questionnaire_with_questions(self, question_set):
        self.form_model.delete_all_fields()

        if self.form_model.entity_defaults_to_reporter():
            self.form_model.add_field(self._create_entity_id_question_for_activity_report())

        for question in question_set:
            self.form_model.add_field(self._create_question(question))


    def _create_question(self, post_dict):
        options = post_dict.get('options')
        datadict_type = options.get('ddtype') if options is not None else None
        if is_not_empty(datadict_type):
            #  question already has a data dict type
            datadict_slug = datadict_type.get('slug')
        else:
            datadict_slug = str(slugify(unicode(post_dict.get('title'))))
        ddtype = self._get_or_create_data_dict(name=post_dict.get('code'), slug=datadict_slug,
            primitive_type=post_dict.get('type'), description=post_dict.get('title'))

        if post_dict["type"] == "text":
            return self._create_text_question(post_dict, ddtype)
        if post_dict["type"] == "integer":
            return self._create_integer_question(post_dict, ddtype)
        if post_dict["type"] == "geocode":
            return self._create_geo_code_question(post_dict, ddtype)
        if post_dict["type"] == "select":
            return self._create_select_question(post_dict, single_select_flag=False, ddtype=ddtype)
        if post_dict["type"] == "date":
            return self._create_date_question(post_dict, ddtype)
        if post_dict["type"] == "select1":
            return self._create_select_question(post_dict, single_select_flag=True, ddtype=ddtype)

    def _get_or_create_data_dict(self, name, slug, primitive_type, description=None):
        try:
            #  Check if is existing
            ddtype = get_datadict_type_by_slug(self.dbm, slug)
        except DataObjectNotFound:
            #  Create new one
            ddtype = create_datadict_type(dbm=self.dbm, name=name, slug=slug,
                primitive_type=primitive_type, description=description)
        return ddtype

    def _create_entity_id_question_for_activity_report(self):
        entity_data_dict_type = self._get_or_create_data_dict(name="eid", slug="entity_id", primitive_type="string",
            description="Entity ID")
        name = ugettext("I am submitting this data on behalf of")
        entity_id_question = TextField(name=name, code='eid',
            label=name,
            entity_question_flag=True, ddtype=entity_data_dict_type,
            constraints=[TextLengthConstraint(min=1, max=12)],
            instruction=ugettext("Choose Data Sender from this list."))
        return entity_id_question


    def _create_text_question(self, post_dict, ddtype):
        max_length_from_post = post_dict.get("max_length")
        min_length_from_post = post_dict.get("min_length")
        max_length = max_length_from_post if not is_empty(max_length_from_post) else None
        min_length = min_length_from_post if not is_empty(min_length_from_post) else None
        constraints = []
        if not (max_length is None and min_length is None):
            constraints.append(TextLengthConstraint(min=min_length, max=max_length))
        return TextField(name=post_dict["title"], code=post_dict["code"].strip(), label=post_dict["title"],
            entity_question_flag=post_dict.get("is_entity_question"), constraints=constraints, ddtype=ddtype,
            instruction=post_dict.get("instruction"), required=post_dict.get("required"))


    def _create_integer_question(self, post_dict, ddtype):
        max_range_from_post = post_dict.get("range_max")
        min_range_from_post = post_dict.get("range_min")
        max_range = max_range_from_post if not is_empty(max_range_from_post) else None
        min_range = min_range_from_post if not is_empty(min_range_from_post) else None
        range = NumericRangeConstraint(min=min_range, max=max_range)
        return IntegerField(name=post_dict["title"], code=post_dict["code"].strip(), label=post_dict["title"],
            constraints=[range], ddtype=ddtype, instruction=post_dict.get("instruction"),
            required=post_dict.get("required"))


    def _create_date_question(self, post_dict, ddtype):
        return DateField(name=post_dict["title"], code=post_dict["code"].strip(), label=post_dict["title"],
            date_format=post_dict.get('date_format'), ddtype=ddtype, instruction=post_dict.get("instruction"),
            required=post_dict.get("required"), event_time_field_flag=post_dict.get('event_time_field_flag', False))


    def _create_geo_code_question(self, post_dict, ddtype):
        return GeoCodeField(name=post_dict["title"], code=post_dict["code"].strip(), label=post_dict["title"],
            ddtype=ddtype,
            instruction=post_dict.get("instruction"), required=post_dict.get("required"))


    def _create_select_question(self, post_dict, single_select_flag, ddtype):
        options = [(choice.get("text"), choice.get("val")) for choice in post_dict["choices"]]
        return SelectField(name=post_dict["title"], code=post_dict["code"].strip(), label=post_dict["title"],
            options=options, single_select_flag=single_select_flag, ddtype=ddtype,
            instruction=post_dict.get("instruction"), required=post_dict.get("required"))

