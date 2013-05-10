import unittest
import django
from django.core.exceptions import ValidationError
from django.forms.fields import CharField, MultipleChoiceField, ChoiceField, RegexField
from mangrove.datastore.datadict import DataDictType
from mangrove.form_model.field import TextField, SelectField, field_attributes, HierarchyField, TelephoneNumberField, IntegerField
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.form_model import FormModel, LOCATION_TYPE_FIELD_NAME, LOCATION_TYPE_FIELD_CODE
from mock import Mock, patch, self
from mangrove.form_model.validation import TextLengthConstraint, RegexConstraint, NumericRangeConstraint
from datawinners.common.constant import DEFAULT_LANGUAGE, FRENCH_LANGUAGE
from datawinners.project.web_questionnaire_form_creator import WebQuestionnaireFormCreator, SubjectQuestionFieldCreator
from datawinners.entity.fields import PhoneNumberField
from datawinners.questionnaire.helper import make_clean_geocode_method

class TestWebQuestionnaireFormCreator(unittest.TestCase):
    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)
        self.form_code = "form_code"
        self._get_form_model()
        self.field_name = "test"
        self.short_code_question_code = "short_code_question_field_name"
        self.field_code = "code"
        self.instruction = "some instruction"
        self.text_field_code = "text"
        self.select_field_code = "select"
        self.get_geo_code_field_question_code_patch = patch(
            'datawinners.project.web_questionnaire_form_creator.get_geo_code_fields_question_code')

        self.get_geo_code_field_question_code_mock = self.get_geo_code_field_question_code_patch.start()
        self.geo_code = 'g'
        self.get_geo_code_field_question_code_mock.return_value = [self.geo_code]
        self.clean_geocode = make_clean_geocode_method(self.geo_code)

    def tearDown(self):
        self.get_geo_code_field_question_code_patch.stop()

    def test_should_create_web_questionnaire_for_char_field(self):
        form_model = self._get_form_model()
        is_required = True
        form_model.add_field(self._get_text_field(is_required, False))

        questionnaire_form_class = WebQuestionnaireFormCreator(None, form_model=form_model).create()

        web_text_field = questionnaire_form_class().fields[self.text_field_code]
        self.assertEqual(CharField, type(web_text_field))
        self.assertEqual(self.field_name, web_text_field.label)
        self.assertEqual(self.instruction, web_text_field.help_text)
        self.assertEqual(is_required, web_text_field.required)
        self.assertTrue(web_text_field.widget.attrs['watermark'] is not None)
        self.assertEqual('padding-top: 7px;', web_text_field.widget.attrs['style'])

    def test_should_create_web_questionnaire_form_model_field(self):
        form_model = self._get_form_model()

        questionnaire_form_class = WebQuestionnaireFormCreator(None, form_model=form_model).create()

        web_questionnaire = questionnaire_form_class()
        self.assertEqual(form_model, web_questionnaire.form_model)

    def test_should_create_web_questionnaire_for_char_field_for_french_language(self):
        form_model = self._get_form_model()
        is_required = True
        form_model.activeLanguages = [FRENCH_LANGUAGE]
        form_model.add_field(self._get_text_field(is_required, False))

        questionnaire_form_class = WebQuestionnaireFormCreator(None, form_model=form_model).create()

        web_text_field = questionnaire_form_class().fields[self.text_field_code]
        self.assertEqual(CharField, type(web_text_field))
        self.assertEqual(self.field_name, web_text_field.label)
        self.assertEqual(web_text_field.max_length, 20)
        self.assertEqual(web_text_field.min_length, 1)

    def test_should_create_web_questionnaire_for_location_field(self):
        form_model = self._get_form_model()
        form_model.add_field(self._get_location_field())

        questionnaire_form_class = WebQuestionnaireFormCreator(None, form_model=form_model).create()

        web_location_field = questionnaire_form_class().fields[LOCATION_TYPE_FIELD_CODE]
        self.assertEqual(CharField, type(web_location_field))
        self.assertTrue(web_location_field.widget.attrs['watermark'] is not None)
        self.assertEqual('padding-top: 7px;', web_location_field.widget.attrs['style'])
        self.assertEqual('location_field', web_location_field.widget.attrs['class'])

    def test_should_append_country_in_location_field(self):
        form_model = self._get_form_model()
        form_model.add_field(self._get_location_field())

        questionnaire_form_class = WebQuestionnaireFormCreator(subject_question_creator=None,
            form_model=form_model).create()
        post_data = {LOCATION_TYPE_FIELD_CODE: 'pune', 'form_code': 'something'}

        web_form = questionnaire_form_class(country="India", data=post_data)
        web_form.is_valid()

        self.assertEqual("pune,India", web_form.cleaned_data[LOCATION_TYPE_FIELD_CODE])


    def test_should_create_web_questionnaire_for_multiple_choice_select_field(self):
        form_model = self._get_form_model()
        is_required = False

        expected_choices, text_field = self._get_select_field(is_required, False)
        form_model.add_field(text_field)

        questionnaire_form_class = WebQuestionnaireFormCreator(None, form_model=form_model).create()

        web_text_field = questionnaire_form_class().fields[self.select_field_code]
        self.assertEqual(MultipleChoiceField, type(web_text_field))
        self.assertEqual(self.field_name, web_text_field.label)
        self.assertEqual(is_required, web_text_field.required)
        self.assertEqual(expected_choices, web_text_field.choices)

    def test_should_create_web_questionnaire_for_single_choice_select_field(self):
        form_model = self._get_form_model()
        is_required = False

        expected_choices, text_field = self._get_select_field(is_required, single_select_flag=True)
        form_model.add_field(text_field)
        expected_choices = [('', '--None--'), ("a", "Red"), ("b", "Green"), ("c", "Blue")]
        questionnaire_form_class = WebQuestionnaireFormCreator(None, form_model=form_model).create()

        web_text_field = questionnaire_form_class().fields[self.select_field_code]
        self.assertEqual(ChoiceField, type(web_text_field))
        self.assertEqual(self.field_name, web_text_field.label)
        self.assertEqual(is_required, web_text_field.required)
        self.assertEqual(expected_choices, web_text_field.choices)

    def test_should_create_hidden_field_for_form_code(self):
        form_model = self._get_form_model()
        questionnaire_form_class = WebQuestionnaireFormCreator(None, form_model=form_model).create()

        web_text_field = questionnaire_form_class().fields['form_code']
        self.assertEqual(CharField, type(web_text_field))
        self.assertEqual(self.form_code, web_text_field.initial)

    def test_should_create_hidden_field_for_entity_id_question_code(self):
        form_model = self._get_form_model()
        questionnaire_form_class = WebQuestionnaireFormCreator(None, form_model=form_model).create()

        web_text_field = questionnaire_form_class().fields['form_code']
        self.assertEqual(CharField, type(web_text_field))
        self.assertEqual(self.form_code, web_text_field.initial)

    def test_should_create_web_questionnaire(self):
        form_model = self._get_form_model()
        subject_code = "subject_code"
        subject_question_code = 'subject_question_code'
        field1 = self._get_text_field(True, True, subject_code)
        form_model.add_field(field1)
        field2 = self._get_text_field(False, False)
        form_model.add_field(field2)
        field3 = self._get_select_field(False, False, 'test 2')[1]
        form_model.add_field(field3)
        subject_question_creator_mock = Mock(spec=SubjectQuestionFieldCreator)
        subject_question_creator_mock.create.return_value = ChoiceField()
        subject_question_creator_mock.create_code_hidden_field.return_value = {subject_question_code: CharField()}

        questionnaire_form_class = WebQuestionnaireFormCreator(subject_question_creator=subject_question_creator_mock,
            form_model=form_model).create()

        web_form = questionnaire_form_class()
        self.assertEqual(5, len(web_form.fields))

        form_code_hidden_field = web_form.fields[self.form_code]
        self.assertEqual(CharField, type(form_code_hidden_field))

        subject_field = web_form.fields[subject_code]
        self.assertEqual(ChoiceField, type(subject_field))

        subject_field = web_form.fields[subject_question_code]
        self.assertEqual(CharField, type(subject_field))

        simple_text_field = web_form.fields[self.text_field_code]
        self.assertEqual(CharField, type(simple_text_field))

        multiple_choice_field = web_form.fields[self.select_field_code]
        self.assertEqual(MultipleChoiceField, type(multiple_choice_field))


    def test_should_give_short_code_question_field_name_for_subject_registration_questionnaire(self):
        form_model = self._get_form_model(is_registration_form=True)
        subject_code = "subject_code"
        form_model.add_field(self._get_text_field(True, True, subject_code))
        questionnaire_form_class = WebQuestionnaireFormCreator(subject_question_creator=None,
            form_model=form_model).create()
        self.assertEqual(subject_code, questionnaire_form_class().short_code_question_code)

    def test_should_short_code_question_class_for_subject_registration_questionnaire(self):
        form_model = self._get_form_model(is_registration_form=True)
        subject_code = "subject_code"
        form_model.add_field(self._get_text_field(True, True, subject_code))
        questionnaire_form_class = WebQuestionnaireFormCreator(subject_question_creator=None,
            form_model=form_model).create()
        self.assertEqual('subject_field', questionnaire_form_class().fields[subject_code].widget.attrs['class'])


    def test_should_pre_populate_datasenders_for_subject_question(self):
        subject_field = self._get_text_field(True, True)
        project = self._get_mock_project()
        display_subject_field = SubjectQuestionFieldCreator(self.dbm, project).create(subject_field)
        self.assertEqual(ChoiceField, type(display_subject_field))
        expected_choices = [('a', 'reporter1  (a)'), ('b', 'reporter2  (b)')]
        self.assertEqual(expected_choices, display_subject_field.choices)

    def test_should_pre_populate_choices_for_subject_question_on_basis_of_entity_type(self):
        expected_code = "expected_code"
        subject_field = self._get_text_field(True, True, expected_code)
        project = self._get_mock_project()
        project_subject_loader_mock = Mock()
        fields = ['name', 'short_code']
        label = None
        project_subject_loader_mock.return_value = [{'short_code': 'a', 'cols': ['clinic1', 'a']},
                                                    {'short_code': 'b', 'cols': ['clinic2', 'b']},
                                                   ], fields, label
        project.entity_type.return_value = ["Clinic"]
        project.is_on_type.return_value = False
        expected_choices = [('a', 'clinic1  (a)'), ('b', 'clinic2  (b)')]
        display_subject_field = SubjectQuestionFieldCreator(self.dbm, project,
            project_subject_loader=project_subject_loader_mock).create(subject_field)

        self.assertEqual(expected_choices, display_subject_field.choices)

        subject_question_code_hidden_field_dict = SubjectQuestionFieldCreator(self.dbm, project,
            project_subject_loader=project_subject_loader_mock).create_code_hidden_field(subject_field)

        self.assertEqual(expected_code, subject_question_code_hidden_field_dict['entity_question_code'].label)

    def test_should_create_django_phone_number_field(self):
        form_model = self._get_form_model()
        form_model.add_field(self._get_telephone_number_field())
        questionnaire_form_class = WebQuestionnaireFormCreator(None, form_model=form_model).create()
        django_phone_number_field = questionnaire_form_class().fields['m']

        self.assertEqual(PhoneNumberField, type(django_phone_number_field))

    def test_should_create_django_integer_number_field(self):
        form_model = self._get_form_model()
        form_model.add_field(self._get_integer_field())
        questionnaire_form_class = WebQuestionnaireFormCreator(None, form_model=form_model).create()
        django_integer_field = questionnaire_form_class().fields['ag']

        self.assertEqual(django.forms.fields.FloatField, type(django_integer_field))
        self.assertEqual(django_integer_field.max_value, 100)
        self.assertEqual(django_integer_field.min_value, 18)

    def test_should_validate_gps_code_and_return_error_if_only_longitude_is_passed(self):
        mock = Mock()
        mock.cleaned_data = {self.geo_code: '1'}
        with self.assertRaises(ValidationError):
            self.clean_geocode(mock)

    def test_should_validate_gps_code_and_return_error_if_gps_code_is_incorrect(self):
        mock = Mock()
        mock.cleaned_data = {self.geo_code: 'a,b'}
        with self.assertRaises(ValidationError):
            self.clean_geocode(mock)
        mock.cleaned_data = {self.geo_code: '200,300'}
        with self.assertRaises(ValidationError):
            self.clean_geocode(mock)


    def test_should_validate_gps_code_and_should_not_return_error_if_correct_gps_code(self):
        mock = Mock()
        mock.cleaned_data = {self.geo_code: '10,20'}
        self.assertEqual(mock.cleaned_data[self.geo_code], self.clean_geocode(mock))


    def _get_select_field(self, is_required, single_select_flag, label='test'):
        choices = [("Red", "a"), ("Green", "b"), ("Blue", "c")]
        expected_choices = [("a", "Red"), ("b", "Green"), ("c", "Blue")]
        text_field = SelectField(name=label, code=self.select_field_code, label=label,
            ddtype=Mock(spec=DataDictType),
            options=choices, single_select_flag=single_select_flag, required=is_required)
        text_field.value = "Red,Green,Blue"
        return expected_choices, text_field


    def _get_text_field(self, is_required, entity_question_flag, code=None):
        code = self.text_field_code if code is None else code
        field_name = self.field_name if not entity_question_flag else self.short_code_question_code
        text_field = TextField(name=field_name, code=code, label=field_name,
            ddtype=Mock(spec=DataDictType),
            instruction=self.instruction, required=is_required, constraints=[TextLengthConstraint(1, 20)],
            entity_question_flag=entity_question_flag)
        return text_field


    def _get_location_field(self):
        location_field = HierarchyField(name=LOCATION_TYPE_FIELD_NAME, code=LOCATION_TYPE_FIELD_CODE,
            label=self.field_name, ddtype=Mock(spec=DataDictType))

        return location_field


    def _get_telephone_number_field(self):
        form_model = self._get_form_model()
        phone_number_field = TelephoneNumberField(name=self.field_name, code='m', label=self.field_name,
            ddtype=Mock(spec=DataDictType),
            constraints=[TextLengthConstraint(max=15), RegexConstraint(reg='^[0-9]+$')])
        return phone_number_field


    def _get_integer_field(self):
        integer_field = IntegerField(name=self.field_name, code='ag', label=self.field_name,
            ddtype=Mock(spec=DataDictType), constraints=[NumericRangeConstraint(min=18, max=100)])
        return integer_field


    def _get_mock_project(self):
        project = Mock()
        data_senders = [{field_attributes.NAME: 'reporter1', 'short_code': 'a'},
                        {field_attributes.NAME: 'reporter2', 'short_code': 'b'},
        ]
        project.get_data_senders.return_value = data_senders
        return project


    def _get_form_model(self, is_registration_form=False):
        return FormModel(dbm=self.dbm, form_code=self.form_code, name="abc", fields=[],
            is_registration_model=is_registration_form, entity_type=["entity_type"])

    def test_should_create_regex_field_for_short_code_question_if_registration(self):
        form_model = self._get_form_model(True)

        is_required = True
        form_model.add_field(self._get_text_field(is_required, False))
        with patch.object(WebQuestionnaireFormCreator, '_get_short_code_question_code') as get_short_code_qestion_code:
            get_short_code_qestion_code.return_value = {u'short_code_question_code': self.text_field_code}
            questionnaire_form_class = WebQuestionnaireFormCreator(None, form_model=form_model).create()

            web_text_field = questionnaire_form_class().fields[self.text_field_code]
            self.assertEqual(RegexField, type(web_text_field))

    def test_create_subject_unique_id_field_with_constraints(self):
        ddtype = DataDictType(self.dbm, name=u'Name', primitive_type=u'string', constraints={})
        constraints = [TextLengthConstraint(max=20)]
        field = TextField("short_code", "q6", "'What is the clinic\\'s Unique ID Number?'", ddtype, constraints,
            'entity_question_flag')
        dictionary = WebQuestionnaireFormCreator(None, None)._get_short_code_django_field(field)
        self.assertEqual(20, dictionary.get('q6').max_length)
        self.assertIsNone(dictionary.get('q6').min_length)


    def test_should_make_short_code_field_readonly_for_subject_edition(self):
        form_model = self._get_form_model(is_registration_form=True)
        subject_code = "subject_code"
        form_model.add_field(self._get_text_field(True, True, subject_code))
        questionnaire_form_class = WebQuestionnaireFormCreator(subject_question_creator=None,
            form_model=form_model, is_update=True).create()
        self.assertEqual('readonly', questionnaire_form_class().fields[subject_code].widget.attrs['readonly'])