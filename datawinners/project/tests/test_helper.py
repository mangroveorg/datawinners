# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
from mock import Mock, patch
from datawinners.project import helper
from datawinners.project.models import Project
from datawinners.project.views import _get_imports_subjects_post_url
from mangrove.datastore.database import  DatabaseManager
from mangrove.datastore.datadict import DataDictType
from mangrove.errors.MangroveException import DataObjectNotFound, FormModelDoesNotExistsException
from mangrove.form_model.field import TextField, IntegerField, SelectField, DateField, GeoCodeField
from mangrove.form_model.form_model import FormModel
from mangrove.datastore import data
from copy import copy
from mangrove.datastore.aggregrate import Sum, Latest
from mangrove.form_model.validation import TextLengthConstraint, NumericRangeConstraint


class TestHelper(unittest.TestCase):
    def setUp(self):
        self.patcher1 = patch("datawinners.project.helper.create_datadict_type")
        self.patcher2 = patch("datawinners.project.helper.get_datadict_type_by_slug")
        self.create_ddtype_mock = self.patcher1.start()
        self.get_datadict_type_by_slug_mock = self.patcher2.start()
        self.create_ddtype_mock.return_value = Mock(spec=DataDictType)
        self.get_datadict_type_by_slug_mock.side_effect = DataObjectNotFound("", "", "")
        self.dbm = Mock(spec=DatabaseManager)


    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()


    def test_should_return_code_title_tuple_list(self):
        ddtype = Mock(spec=DataDictType)
        question1 = TextField(label="entity_question", code="ID", name="What is associated entity",
                              language="en", entity_question_flag=True, ddtype=ddtype)
        question2 = TextField(label="question1_Name", code="Q1", name="What is your name",
                              defaultValue="some default value", language="eng", ddtype=ddtype)
        code_and_title = [(each_field.code, each_field.name)for each_field in [question1, question2]]
        self.assertEquals([("ID", "What is associated entity"), ("Q1", "What is your name")], code_and_title)

    def test_should_create_questionnaire_with_entity_question_for_subjects(self):
        NAME = "eid"
        LABEL = "Entity ID"
        SLUG = "entity_id"
        TYPE = "string"
        post = {"entity_type": "Water Point", "name": "Test Project", "language": "en"}
        dbm = Mock(spec=DatabaseManager)

        patcher = patch("datawinners.project.helper.generate_questionnaire_code")
        mock = patcher.start()
        mock.return_value = '001'

        expected_data_dict = DataDictType(dbm, NAME, SLUG, TYPE, LABEL)
        self.create_ddtype_mock.return_value = expected_data_dict

        with patch("datawinners.project.helper.get_datadict_type_by_slug") as get_datadict_type_by_slug_mock:
            get_datadict_type_by_slug_mock.side_effect = DataObjectNotFound("", "", "")
            form_model = helper.create_questionnaire(post, dbm)

        self.create_ddtype_mock.assert_called_twice_with(dbm=dbm, name=NAME, slug=SLUG,
                                                         primitive_type=TYPE, description=LABEL)
        self.assertEqual(expected_data_dict, form_model.fields[0].ddtype)

        self.assertEqual(2, len(form_model.fields))

        self.assertTrue(form_model.fields[0].is_entity_field)
        self.assertTrue(form_model.fields[0].is_required())
        self.assertEqual('q1',form_model.fields[0].code)

        activity_period_question = form_model.fields[1]
        self.assertTrue(activity_period_question.is_required())
        self.assertEqual('q2',activity_period_question.code)

        self.assertEqual(["Water Point"], form_model.entity_type)
        self.assertFalse(form_model.is_active())
        patcher.stop()

    def test_should_create_questionnaire_with_entity_question_for_questionnaire_on_activity_report(self):
        NAME = "eid"
        LABEL = "Entity ID"
        SLUG = "entity_id"
        TYPE = "string"
        post = {"entity_type": "reporter", "name": "Test Project", "language": "en"}
        dbm = Mock(spec=DatabaseManager)

        patcher = patch("datawinners.project.helper.generate_questionnaire_code")
        mock = patcher.start()
        mock.return_value = '001'

        expected_data_dict = DataDictType(dbm, NAME, SLUG, TYPE, LABEL)
        self.create_ddtype_mock.return_value = expected_data_dict

        with patch("datawinners.project.helper.get_datadict_type_by_slug") as get_datadict_type_by_slug_mock:
            get_datadict_type_by_slug_mock.side_effect = DataObjectNotFound("", "", "")
            form_model = helper.create_questionnaire(post, dbm)

        self.create_ddtype_mock.assert_called_twice_with(dbm=dbm, name=NAME, slug=SLUG,
                                                         primitive_type=TYPE, description=LABEL)

        self.assertEqual(2, len(form_model.fields))

        entity_id_field = form_model.fields[0]
        self.assertEqual(expected_data_dict, entity_id_field.ddtype)
        self.assertTrue(entity_id_field.is_entity_field)
        self.assertTrue(entity_id_field.is_required())
        self.assertEqual(NAME, entity_id_field.code)

        activity_period_question = form_model.fields[1]
        self.assertTrue(activity_period_question.is_required())
        self.assertEqual('q1',activity_period_question.code)

        self.assertFalse(form_model.is_active())
        patcher.stop()


    def test_should_generate_unique_questionnaire_code(self):
        patcher = patch("datawinners.project.helper.models")
        models_mock = patcher.start()
        patcher1 = patch("datawinners.project.helper.get_form_model_by_code")
        form_code_mock = patcher1.start()
        dbm = Mock(spec=DatabaseManager)

        form_code_mock.side_effect = FormModelDoesNotExistsException('')
        models_mock.count_projects.return_value = 0
        self.assertEqual(helper.generate_questionnaire_code(dbm), "001")

        myproject = Mock(spec=Project)
        models_mock.count_projects.return_value = 1
        self.assertEqual(helper.generate_questionnaire_code(dbm), "002")

        patcher.stop()
        patcher1.stop()

    def test_should_generate_next_questionnaire_code_if_code_already_exists(self):
        patcher = patch("datawinners.project.helper.models")
        models_mock = patcher.start()

        patcher1 = patch("datawinners.project.helper.get_form_model_by_code")
        form_code_mock = patcher1.start()

        dbm = Mock(spec=DatabaseManager)

        myproject = Mock(spec=Project)
        models_mock.count_projects.return_value = 1

        def expected_side_effect(*args, **kwargs):
            code = kwargs.get('code') or args[1]
            if code == "003":
                raise FormModelDoesNotExistsException('')
            if code == "002":
                return Mock(spec=FormModel)

        form_code_mock.side_effect = expected_side_effect

        self.assertEqual(helper.generate_questionnaire_code(dbm), "003")

        patcher.stop()
        patcher1.stop()


    def test_should_create_header_list(self):
        ddtype = Mock(spec=DataDictType)
        question1 = TextField(label="What is associated entity", code="ID", name="What is associated entity",
                              language="en", entity_question_flag=True, ddtype=ddtype)
        question2 = TextField(label="What is your name", code="Q1", name="What is your name",
                              defaultValue="some default value", language="en", ddtype=ddtype)

        form_model = Mock()
        form_model.fields = [question1, question2]
        form_model.entity_type = ["Clinic"]
        form_model.activeLanguages = ['en']

        actual_list = helper.get_headers(form_model)
        self.assertListEqual(["Clinic Code", "What is your name"], actual_list)

    def test_should_create_value_list(self):
        data_dictionary = {'1': {'What is age of father?': 55, 'What is your name?': 'shweta',
                                 "What colour do you choose?": ["red", "blue"],
                                 "what is your loc?": [21.1, 23.3],
                                 'What is associated entity?': 'cid002'},
                           '2': {'What is age of father?': 35, 'What is your name?': 'asif',
                                 "What colour do you choose?": ["red"], "what is your loc?": [21.1],
                                 'What is associated entity?': 'cid001'}}
        header_list = ["Clinic code?", "What is your name?", "What is age of father?",
                       "What colour do you choose?", "what is your loc?"]
        field_valus, grand_totals = helper.get_all_values(data_dictionary, header_list, 'What is associated entity?')
        expected_list = [["cid002", 'shweta', 55, "red,blue", "21.1,23.3"],
            ["cid001", 'asif', 35, "red", "21.1"]]
        self.assertListEqual(expected_list, field_valus)

    def test_should_create_type_list(self):
        ddtype = Mock(spec=DataDictType)
        question1 = IntegerField(label="number_question", code="ID", name="How many beds",
                                 language="eng", ddtype=ddtype)
        question2 = TextField(label="question1_Name", code="Q1", name="What is your name",
                              defaultValue="some default value", language="eng", ddtype=ddtype)
        question3 = SelectField(label="multiple_choice_question", code="Q2",
                                options=[("red", 1), ("yellow", 2), ('green', 3)], name="What is your favourite colour",
                                ddtype=ddtype)
        question4 = DateField("What is date", "Q4", "date_question", "mm.yyyy", ddtype)
        actual_list = helper.get_aggregation_options_for_all_fields([question1, question2, question3, question4])
        choice_type = copy(helper.MULTI_CHOICE_TYPE_OPTIONS)
        expected_list = [helper.NUMBER_TYPE_OPTIONS, helper.TEXT_TYPE_OPTIONS, choice_type, helper.DATE_TYPE_OPTIONS]
        self.assertListEqual(expected_list, actual_list)

    def test_should_return_aggregates_dictionary(self):
        header_list = ["field1", "field2"]
        post_data = ["Latest", "Sum"]
        expected_dictionary = {"field1": data.reduce_functions.LATEST, "field2": data.reduce_functions.SUM}
        actual_dict = helper.get_aggregate_dictionary(header_list, post_data)
        self.assertEquals(expected_dictionary, actual_dict)

    def test_should_return_aggregates_list(self):
        field_mock = Mock()
        field_mock.name = "field1"
        field_mock1 = Mock()
        field_mock1.name = "field2"
        post_data = ["Latest", "Sum"]
        actual_list = helper.get_aggregate_list([field_mock, field_mock1], post_data)
        self.assertIsInstance(actual_list[0], Latest)
        self.assertIsInstance(actual_list[1], Sum)

    def test_should_return_formatted_time_string(self):
        expected_val = "01-01-2011 00:00:00"
        self.assertEquals(expected_val, helper.get_formatted_time_string("01-01-2011 00:00:00"))


class TestPreviewCreator(unittest.TestCase):
    def test_should_create_basic_fields_in_preview(self):
        type = DataDictType(Mock(DatabaseManager), name="Name type")
        field = TextField(name="What's in a name?", code="nam", label="naam", ddtype=type,
                          instruction="please write more tests")
        preview = helper.get_preview_for_field(field)
        self.assertEquals("What's in a name?", preview["description"])
        self.assertEquals("nam", preview["code"])
        self.assertEquals("text", preview["type"])
        self.assertEquals("please write more tests", preview["instruction"])


    def test_should_add_constraint_text_for_text_field_with_min(self):
        type = DataDictType(Mock(DatabaseManager), name="Name type")
        constraints = [TextLengthConstraint(min=10)]
        field = TextField(name="What's in a name?", code="nam", label="naam", ddtype=type, constraints=constraints)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("Minimum 10 characters", preview["constraints"])

    def test_should_add_constraint_text_for_text_field_with_max(self):
        type = DataDictType(Mock(DatabaseManager), name="Name type")
        constraints = [TextLengthConstraint(max=100)]
        field = TextField(name="What's in a name?", code="nam", label="naam", ddtype=type, constraints=constraints)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("Upto 100 characters", preview["constraints"])

    def test_should_add_constraint_text_for_text_field_with_max_and_min(self):
        type = DataDictType(Mock(DatabaseManager), name="Name type")
        constraints = [TextLengthConstraint(min=10, max=100)]
        field = TextField(name="What's in a name?", code="nam", label="naam", ddtype=type, constraints=constraints)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("Between 10 -- 100 characters", preview["constraints"])

    def test_should_add_constraint_text_for_text_field_without_constraint(self):
        type = DataDictType(Mock(DatabaseManager), name="Name type")
        field = TextField(name="What's in a name?", code="nam", label="naam", ddtype=type)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("", preview["constraints"])


    def test_should_add_constraint_text_for_numeric_field_with_min(self):
        type = DataDictType(Mock(DatabaseManager), name="age type")
        constraint = NumericRangeConstraint(min=10)
        field = IntegerField(name="What's in the age?", code="nam", label="naam", ddtype=type, constraints=[constraint])
        preview = helper.get_preview_for_field(field)
        self.assertEqual("Minimum 10", preview["constraints"])
        self.assertEqual("integer", preview["type"])

    def test_should_add_constraint_text_for_numeric_field_with_max(self):
        type = DataDictType(Mock(DatabaseManager), name="age type")
        constraint = NumericRangeConstraint(max=100)
        field = IntegerField(name="What's in the age?", code="nam", label="naam", ddtype=type, constraints=[constraint])
        preview = helper.get_preview_for_field(field)
        self.assertEqual("Upto 100", preview["constraints"])

    def test_should_add_constraint_text_for_numeric_field_with_max_and_min(self):
        type = DataDictType(Mock(DatabaseManager), name="age type")
        constraint = NumericRangeConstraint(min=10, max=100)
        field = IntegerField(name="What's in the age?", code="nam", label="naam", ddtype=type, constraints=[constraint])
        preview = helper.get_preview_for_field(field)
        self.assertEqual("10 -- 100", preview["constraints"])

    def test_should_add_constraint_text_for_numeric_field_without_constraint(self):
        type = DataDictType(Mock(DatabaseManager), name="age type")
        field = IntegerField(name="What's in the age?", code="nam", label="naam", ddtype=type)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("", preview["constraints"])

    def test_should_return_choices(self):
        type = DataDictType(Mock(DatabaseManager), name="color type")
        field = SelectField(name="What's the color?", code="nam", label="naam", ddtype=type,
                            options=[("Red", "a"), ("Green", "b"), ("Blue", "c")])
        preview = helper.get_preview_for_field(field)
        self.assertEqual("select1", preview["type"])
        self.assertEqual(["Red", "Green", "Blue"], preview["constraints"])

    def test_should_return_choices_type_as_select(self):
        type = DataDictType(Mock(DatabaseManager), name="color type")
        field = SelectField(name="What's the color?", code="nam", label="naam", ddtype=type,
                            options=[("Red", "a"), ("Green", "b"), ("Blue", "c")], single_select_flag=False)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("select", preview["type"])

    def test_should_return_date_format(self):
        type = DataDictType(Mock(DatabaseManager), name="date type")
        field = DateField(name="What is the date?", code="dat", label="naam", ddtype=type, date_format="dd/mm/yyyy")
        preview = helper.get_preview_for_field(field)
        self.assertEqual("dd/mm/yyyy", preview["constraints"])

    def test_should_return_geocode_format(self):
        type = DataDictType(Mock(DatabaseManager), name="date type")
        field = GeoCodeField(name="What is the place?", code="dat", label="naam", ddtype=type)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("xx.xxxx yy.yyyy", preview["constraints"])

    def test_should_make_project_post_url_for_import_subject_project_wizard(self):
        url = _get_imports_subjects_post_url('123')
        self.assertEqual("/entity/subject/import/?project_id=123", url)

    def test_should_make_the_post_url_for_import_subject_project_wizard(self):
        url = _get_imports_subjects_post_url()
        self.assertEqual("/entity/subject/import/", url)