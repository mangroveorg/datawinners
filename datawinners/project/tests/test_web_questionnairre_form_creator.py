import unittest
from django.forms.fields import CharField, MultipleChoiceField, ChoiceField, RegexField
from mangrove.datastore.datadict import DataDictType
from mangrove.form_model.field import TextField, SelectField, field_attributes, HierarchyField, TelephoneNumberField
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.form_model import FormModel, LOCATION_TYPE_FIELD_NAME, LOCATION_TYPE_FIELD_CODE
from mock import Mock
from mangrove.form_model.validation import TextLengthConstraint, RegexConstraint
from project.web_questionnaire_form_creator import WebQuestionnaireFormCreater, SubjectQuestionFieldCreator

class TestWebQuestionnaireFormCreator(unittest.TestCase):
    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)
        self.form_code="form_code"
        self.form_model = FormModel(dbm=self.dbm,form_code=self.form_code,name="abc",fields=[])
        self.field_name = "test"
        self.field_code = "code"
        self.instruction = "some instruction"
        self.text_field_code="text"
        self.select_field_code="select"


    def test_should_create_web_questionnaire_for_char_field(self):
        is_required = True
        self.form_model.add_field(self._get_text_field(is_required,False))

        questionnaire_form_class = WebQuestionnaireFormCreater(None,form_model=self.form_model).create()

        web_text_field = questionnaire_form_class().fields[self.text_field_code]
        self.assertEqual(CharField,type(web_text_field))
        self.assertEqual(self.field_name,web_text_field.label)
        self.assertEqual(self.instruction,web_text_field.help_text)
        self.assertEqual(is_required,web_text_field.required)
        self.assertTrue(web_text_field.widget.attrs['watermark'] is not None)
        self.assertEqual('padding-top: 7px;',web_text_field.widget.attrs['style'])

    def test_should_create_web_questionnaire_for_location_field(self):
        self.form_model.add_field(self._get_location_field())

        questionnaire_form_class = WebQuestionnaireFormCreater(None,form_model=self.form_model).create()

        web_location_field = questionnaire_form_class().fields[LOCATION_TYPE_FIELD_CODE]
        self.assertEqual(CharField,type(web_location_field))
        self.assertTrue(web_location_field.widget.attrs['watermark'] is not None)
        self.assertEqual('padding-top: 7px;',web_location_field.widget.attrs['style'])
        self.assertEqual('location_field',web_location_field.widget.attrs['class'])


    def test_should_create_web_questionnaire_for_multiple_choice_select_field(self):
        is_required = False

        expected_choices, text_field = self._get_select_field(is_required,False)
        self.form_model.add_field(text_field)

        questionnaire_form_class = WebQuestionnaireFormCreater(None,form_model=self.form_model).create()

        web_text_field = questionnaire_form_class().fields[self.select_field_code]
        self.assertEqual(MultipleChoiceField,type(web_text_field))
        self.assertEqual(self.field_name,web_text_field.label)
        self.assertEqual(is_required,web_text_field.required)
        self.assertEqual(expected_choices,web_text_field.choices)

    def test_should_create_web_questionnaire_for_single_choice_select_field(self):
        is_required = False

        expected_choices, text_field = self._get_select_field(is_required,single_select_flag=True)
        self.form_model.add_field(text_field)
        expected_choices = [('', '--None--'),("a", "Red"), ("b", "Green"), ("c", "Blue")]
        questionnaire_form_class = WebQuestionnaireFormCreater(None,form_model=self.form_model).create()

        web_text_field = questionnaire_form_class().fields[self.select_field_code]
        self.assertEqual(ChoiceField,type(web_text_field))
        self.assertEqual(self.field_name,web_text_field.label)
        self.assertEqual(is_required,web_text_field.required)
        self.assertEqual(expected_choices,web_text_field.choices)

    def test_should_create_hidden_field_for_form_code(self):

        questionnaire_form_class = WebQuestionnaireFormCreater(None,form_model=self.form_model).create()

        web_text_field = questionnaire_form_class().fields['form_code']
        self.assertEqual(CharField,type(web_text_field))
        self.assertEqual(self.form_code,web_text_field.initial)

    def test_should_create_hidden_field_for_entity_id_question_code(self):

        questionnaire_form_class = WebQuestionnaireFormCreater(None,form_model=self.form_model).create()

        web_text_field = questionnaire_form_class().fields['form_code']
        self.assertEqual(CharField,type(web_text_field))
        self.assertEqual(self.form_code,web_text_field.initial)

    def test_should_create_web_questionnaire(self):

        subject_code = "subject_code"
        subject_question_code='subject_question_code'
        self.form_model.add_field(self._get_text_field(True,True, subject_code))
        self.form_model.add_field(self._get_text_field(False,False))
        self.form_model.add_field(self._get_select_field(False,False)[1])
        subject_question_creator_mock = Mock(spec=SubjectQuestionFieldCreator)
        subject_question_creator_mock.create.return_value=ChoiceField()
        subject_question_creator_mock.create_code_hidden_field.return_value={subject_question_code:CharField()}

        questionnaire_form_class = WebQuestionnaireFormCreater(subject_question_creator=subject_question_creator_mock,form_model=self.form_model).create()

        web_form = questionnaire_form_class()
        self.assertEqual(5,len(web_form.fields))

        form_code_hidden_field = web_form.fields[self.form_code]
        self.assertEqual(CharField,type(form_code_hidden_field))

        subject_field = web_form.fields[subject_code]
        self.assertEqual(ChoiceField,type(subject_field))

        subject_field = web_form.fields[subject_question_code]
        self.assertEqual(CharField,type(subject_field))

        simple_text_field = web_form.fields[self.text_field_code]
        self.assertEqual(CharField,type(simple_text_field))

        multiple_choice_field = web_form.fields[self.select_field_code]
        self.assertEqual(MultipleChoiceField,type(multiple_choice_field))

    def _get_mock_project(self):
        project = Mock()
        data_senders = [{field_attributes.NAME: 'reporter1', 'short_code': 'a'},
                {field_attributes.NAME: 'reporter2', 'short_code': 'b'},
        ]
        project.get_data_senders.return_value = data_senders
        return project

    def test_should_pre_populate_datasenders_for_subject_question(self):
        subject_field = self._get_text_field(True,True)
        project = self._get_mock_project()
        display_subject_field = SubjectQuestionFieldCreator(self.dbm,project).create(subject_field)
        self.assertEqual(ChoiceField,type(display_subject_field))
        expected_choices = [('a', 'reporter1  (a)'), ('b', 'reporter2  (b)')]
        self.assertEqual(expected_choices,display_subject_field.choices)

    def test_should_pre_populate_choices_for_subject_question_on_basis_of_entity_type(self):
        expected_code = "expected_code"
        subject_field = self._get_text_field(True,True, expected_code)
        project = self._get_mock_project()
        project_subject_loader_mock=Mock()
        fields = ['name', 'short_code']
        label = None
        project_subject_loader_mock.return_value= [{'cols': ['clinic1','a']},
                {'cols': ['clinic2','b']},
        ], fields, label
        project.entity_type.return_value=["Clinic"]
        project.is_on_type.return_value=False
        expected_choices = [('a', 'clinic1  (a)'), ('b', 'clinic2  (b)')]
        display_subject_field = SubjectQuestionFieldCreator(self.dbm,project,project_subject_loader=project_subject_loader_mock).create(subject_field)
        self.assertEqual(expected_choices,display_subject_field.choices)
        subject_question_code_hidden_field_dict = SubjectQuestionFieldCreator(self.dbm,project,project_subject_loader=project_subject_loader_mock).create_code_hidden_field(subject_field)
        self.assertEqual(expected_code,subject_question_code_hidden_field_dict['entity_question_code'].label)



    def _get_select_field(self, is_required,single_select_flag):
        choices = [("Red", "a"), ("Green", "b"), ("Blue", "c")]
        expected_choices = [("a", "Red"), ("b", "Green"), ("c", "Blue")]
        text_field = SelectField(name=self.field_name, code=self.select_field_code, label=self.field_name,
                                 ddtype=Mock(spec=DataDictType),
                                 options=choices, single_select_flag=single_select_flag, required=is_required)
        return expected_choices, text_field

    def _get_text_field(self, is_required,entity_question_flag,code=None):
        code=self.text_field_code if code is None else code
        text_field = TextField(name=self.field_name, code=code, label=self.field_name,
                               ddtype=Mock(spec=DataDictType),
                               instruction=self.instruction, required=is_required,constraints=[TextLengthConstraint(1, 20)],entity_question_flag=entity_question_flag)
        return text_field

    def _get_location_field(self):
        location_field = HierarchyField(name=LOCATION_TYPE_FIELD_NAME, code=LOCATION_TYPE_FIELD_CODE,
                    label=self.field_name,
                    language="en", ddtype=Mock(spec=DataDictType))

        return location_field

    def test_should_create_django_regex_field(self):
        self.form_model.add_field(self._get_telephone_number_field())
        questionnaire_form_class = WebQuestionnaireFormCreater(None,form_model=self.form_model).create()
        django_phone_number_field = questionnaire_form_class().fields['m']

        self.assertEqual(RegexField,type(django_phone_number_field))

    def _get_telephone_number_field(self):
        phone_number_field = TelephoneNumberField(name=self.field_name, code='m', label=self.field_name,
                               ddtype=Mock(spec=DataDictType),
                               constraints=[TextLengthConstraint(max=15), RegexConstraint(reg='^[0-9]+$')])
        return phone_number_field