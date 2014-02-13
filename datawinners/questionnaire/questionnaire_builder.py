from django.utils.translation import ugettext
from mangrove.errors.MangroveException import DataObjectNotFound
from mangrove.form_model.field import IntegerField, TextField, DateField, SelectField, GeoCodeField, TelephoneNumberField, HierarchyField
from mangrove.form_model.form_model import LOCATION_TYPE_FIELD_NAME
from mangrove.form_model.validation import NumericRangeConstraint, TextLengthConstraint, RegexConstraint, ShortCodeRegexConstraint
from mangrove.utils.helpers import slugify
from mangrove.utils.types import is_not_empty, is_empty
from datawinners.entity.helper import question_code_generator

class QuestionnaireBuilder( object ):
    def __init__(self, form_model, dbm, question_builder=None):
        if question_builder is None: question_builder = QuestionBuilder( dbm )
        self.form_model = form_model
        self.question_builder = question_builder
        self.question_code_generator = question_code_generator( )

    def generate_fields_by_question_set(self, max_code, question_set):
        new_fields = []
        if self.form_model.is_entity_type_reporter():
            entity_field = self.question_builder.create_entity_id_question_for_activity_report()
            new_fields.append(entity_field)

        for question in question_set:
            question_code = question['code']
            if question_code == 'code':
                max_code += 1
                question_code = 'q%s' % max_code
            field = self.question_builder.create_question(question, question_code)
            new_fields.append(field)
        return new_fields

    def update_questionnaire_with_questions(self, question_set):
        origin_json_fields = [f._to_json() for f in self.form_model.fields]
        max_code = get_max_code_in_question_set(origin_json_fields or question_set)
        new_fields = self.generate_fields_by_question_set(max_code, question_set)

        self.form_model.create_snapshot()
        self.form_model.delete_all_fields( )
        [self.form_model.add_field(each) for each in new_fields]


class QuestionBuilder( object ):
    def __init__(self, dbm):
        self.dbm = dbm


    def create_question(self, post_dict, code):
        if post_dict["type"] == "text":
            return self._create_text_question( post_dict, code )
        if post_dict["type"] == "integer":
            return self._create_integer_question( post_dict, code )
        if post_dict["type"] == "geocode":
            return self._create_geo_code_question( post_dict, code )
        if post_dict["type"] == "select":
            return self._create_select_question( post_dict, False, code )
        if post_dict["type"] == "date":
            return self._create_date_question( post_dict, code )
        if post_dict["type"] == "select1":
            return self._create_select_question( post_dict, True, code )
        if post_dict["type"] == "telephone_number":
            return self._create_telephone_number_question( post_dict, code )
        if post_dict["type"] == "list":
            return self._create_location_question( post_dict, code )

    def create_entity_id_question_for_activity_report(self):
        entity_id_code = "eid"
        name = ugettext( "I am submitting this data on behalf of" )
        entity_id_question = TextField( name=name, code=entity_id_code,
                                        label=name,
                                        entity_question_flag=True ,
                                        constraints=[TextLengthConstraint( min=1, max=12 )],
                                        instruction=ugettext( "Choose Data Sender from this list." ))
        return entity_id_question


    def _get_name(self, post_dict):
        name = post_dict.get( "name" )
        return name if name is not None else post_dict["title"]

    def _create_text_question(self, post_dict, code):
        max_length_from_post = post_dict.get( "max_length" )
        min_length_from_post = post_dict.get( "min_length" )
        max_length = max_length_from_post if not is_empty( max_length_from_post ) else None
        min_length = min_length_from_post if not is_empty( min_length_from_post ) else None
        constraints = []
        if not (max_length is None and min_length is None):
            constraints.append( TextLengthConstraint( min=min_length, max=max_length ) )
        options = post_dict.get("options")
        if options:
            short_code_constraint = options.get("short_code")
            if short_code_constraint:
                constraints.append(ShortCodeRegexConstraint(short_code_constraint))
        return TextField( name=self._get_name( post_dict ), code=code, label=post_dict["title"],
                          entity_question_flag=post_dict.get( "is_entity_question" ), constraints=constraints ,
                          instruction=post_dict.get( "instruction" ), required=post_dict.get( "required" ))


    def _create_integer_question(self, post_dict, code):
        max_range_from_post = post_dict.get( "range_max" )
        min_range_from_post = post_dict.get( "range_min" )
        max_range = max_range_from_post if not is_empty( max_range_from_post ) else None
        min_range = min_range_from_post if not is_empty( min_range_from_post ) else None
        range = NumericRangeConstraint( min=min_range, max=max_range )
        return IntegerField( name=self._get_name( post_dict ), code=code, label=post_dict["title"],
                             constraints=[range] , instruction=post_dict.get( "instruction" ),
                             required=post_dict.get( "required" ) )


    def _create_date_question(self, post_dict,  code):
        return DateField( name=self._get_name( post_dict ), code=code, label=post_dict["title"],
                          date_format=post_dict.get( 'date_format' ) ,
                          instruction=post_dict.get( "instruction" ),
                          required=post_dict.get( "required" ),
                          event_time_field_flag=post_dict.get( 'event_time_field_flag', False ),)


    def _create_geo_code_question(self, post_dict, code):
        return GeoCodeField( name=self._get_name( post_dict ), code=code, label=post_dict["title"] ,
                             instruction=post_dict.get( "instruction" ), required=post_dict.get( "required" ) )


    def _create_select_question(self, post_dict, single_select_flag, code):
        options = [(choice.get( "text" ), choice.get( "val" )) for choice in post_dict["choices"]]
        return SelectField( name=self._get_name( post_dict ), code=code, label=post_dict["title"],
                            options=options, single_select_flag=single_select_flag ,
                            instruction=post_dict.get( "instruction" ), required=post_dict.get( "required" ) )


    def _create_telephone_number_question(self, post_dict, code):
        return TelephoneNumberField( name=self._get_name( post_dict ), code=code,
                                     label=post_dict["title"] ,
                                     instruction=post_dict.get( "instruction" ), constraints=(
                self._create_constraints_for_mobile_number( )), required=post_dict.get( "required" ) )

    def _create_constraints_for_mobile_number(self):
        mobile_number_length = TextLengthConstraint( max=15 )
        mobile_number_pattern = RegexConstraint( reg='^[0-9]+$' )
        mobile_constraints = [mobile_number_length, mobile_number_pattern]
        return mobile_constraints

    def _create_location_question(self, post_dict, code):
        return HierarchyField( name=LOCATION_TYPE_FIELD_NAME, code=code,
                               label=post_dict["title"] , instruction=post_dict.get( "instruction" ) )

def get_max_code(fields):
    json_fields = [f._to_json() for f in fields]
    return  get_max_code_in_question_set(json_fields)

def get_max_code_in_question_set(question_set):
    codes = [int( q['code'][1:] ) for q in question_set if q['code'].startswith( 'q' )]
    return max( codes ) if codes else 1
