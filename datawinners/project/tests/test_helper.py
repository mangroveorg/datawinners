# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
from django.http import Http404
from mock import Mock, patch
from datawinners.project import helper
from datawinners.project.helper import is_project_exist
from datawinners.project.models import delete_datasenders_from_project, Project
# from datawinners.project.tests.submission_log_data import SUBMISSIONS
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import Entity
from mangrove.errors.MangroveException import DataObjectNotFound, FormModelDoesNotExistsException
from mangrove.form_model.field import TextField, IntegerField, SelectField, DateField, GeoCodeField, Field, UniqueIdField
from mangrove.form_model.form_model import FormModel, FORM_CODE
from mangrove.form_model.validation import TextLengthConstraint, NumericRangeConstraint
from datawinners.scheduler.smsclient import SMSClient
from datawinners.sms.models import MSG_TYPE_USER_MSG


class TestHelper(unittest.TestCase):
    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)


    def test_should_return_code_title_tuple_list(self):
        question1 = UniqueIdField(unique_id_type='clinic',label="entity_question", code="ID", name="What is associated entity")
        question2 = TextField(label="question1_Name", code="Q1", name="What is your name",
                              defaultValue="some default value")
        code_and_title = [(each_field.code, each_field.name) for each_field in [question1, question2]]
        self.assertEquals([("ID", "What is associated entity"), ("Q1", "What is your name")], code_and_title)

    def test_should_generate_unique_questionnaire_code(self):
        patcher = patch("datawinners.project.helper.models")
        models_mock = patcher.start()
        patcher1 = patch("datawinners.project.helper.get_form_model_by_code")
        form_code_mock = patcher1.start()
        dbm = Mock(spec=DatabaseManager)

        form_code_mock.side_effect = FormModelDoesNotExistsException('')
        models_mock.count_projects.return_value = 0
        self.assertEqual(helper.generate_questionnaire_code(dbm), "001")

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

    def test_should_return_formatted_time_string(self):
        expected_val = "01-01-2011 00:00:00"
        self.assertEquals(expected_val, helper.get_formatted_time_string("01-01-2011 00:00:00"))

    def test_should_return_according_value_for_select_field_case_insensitively(self):
        single_select = SelectField(label="multiple_choice_question", code="q", options=[("red", "a"), ("yellow", "b"), ('green', "c")], name="What is your favourite colour")
        multiple_answer = SelectField(label="multiple_choice_question", code="q1", single_select_flag=False,
                                      options=[("value_of_a", "a"), ("value_of_b", "b"), ("value_of_c", 'c' ),
                                               ("d", "d"), ("e", "e"), ('f', "f"),
                                               ("g", "g"), ("h", "h"),
                                               ('i', "i"), ("j", "j"), ("k", "k"), ('l', "l"), ("m", "m"), ("n", "n"),
                                               ('o', "o"),
                                               ("p", "p"), ("q", "q"), ('r', "r"), ("s", "s"), ("t", "t"), ('u', "u"),
                                               ("v", "v"), ("w", "w"),
                                               ('x', "x"), ("y", "y"), ("z", "z"), ("value_of_1a", '1a'),
                                               ("value_of_1b", "1b"),
                                               ("value_of_1c", "1c"), ('1d', "1d")],
                                      name="What is your favourite colour" )
        values = dict({"q": "B", "q1": "b1A1c"})
        single_value = helper.get_according_value(values, single_select)
        multiple_value = helper.get_according_value(values, multiple_answer)
        self.assertEquals(single_value, "yellow")
        self.assertEqual(multiple_value, "value_of_b, value_of_1a, value_of_1c")

    def test_should_return_according_value_for_select_field(self):
        single_select = SelectField(label="multiple_choice_question", code="q",
                                    options=[("red", "a"), ("yellow", "b"), ('green', "c")],
                                    name="What is your favourite colour" )
        multiple_answer = SelectField(label="multiple_choice_question", code="q1", single_select_flag=False,
                                      options=[("value_of_a", "a"), ("value_of_b", "b"), ("value_of_c", 'c' ),
                                               ("d", "d"), ("e", "e"), ('f', "f"),
                                               ("g", "g"), ("h", "h"),
                                               ('i', "i"), ("j", "j"), ("k", "k"), ('l', "l"), ("m", "m"), ("n", "n"),
                                               ('o', "o"),
                                               ("p", "p"), ("q", "q"), ('r', "r"), ("s", "s"), ("t", "t"), ('u', "u"),
                                               ("v", "v"), ("w", "w"),
                                               ('x', "x"), ("y", "y"), ("z", "z"), ("value_of_1a", '1a'),
                                               ("value_of_1b", "1b"),
                                               ("value_of_1c", "1c"), ('1d', "1d")],
                                      name="What is your favourite colour" )
        values = dict({"q": "b", "q1": "b1a1c"})
        single_value = helper.get_according_value(values, single_select)
        multiple_value = helper.get_according_value(values, multiple_answer)
        self.assertEqual(single_value, "yellow")
        self.assertEqual(multiple_value, "value_of_b, value_of_1a, value_of_1c")


    def _get_text_field(self, name):
        return TextField(name, "code", name)

    def _get_form_fields(self):
        eid_field = Mock(spec=UniqueIdField)
        eid_field.code = "eid"
        eid_field.is_event_time_field = False

        na_field = Mock(spec=Field)
        na_field.code = "na"
        na_field.is_event_time_field = False

        fa_field = Mock(spec=Field)
        fa_field.code = "fa"
        fa_field.is_event_time_field = False

        rd_field = Mock(spec=DateField)
        rd_field.code = "rd"
        rd_field.is_event_time_field = True

        bg_field = Mock(spec=Field)
        bg_field.code = "bg"
        bg_field.is_event_time_field = False

        sy_field = Mock(spec=Field)
        sy_field.code = "sy"
        sy_field.is_event_time_field = False

        gps_field = Mock(spec=Field)
        gps_field.code = "gps"
        gps_field.is_event_time_field = False

        rm_field = Mock(spec=Field)
        rm_field.code = "rm"
        rm_field.is_event_time_field = False

        fields = [eid_field, na_field, fa_field, rd_field, bg_field, sy_field, gps_field, rm_field]
        return fields

    def test_should_add_country_code_when_broadcasting_sms_to_other_people(self):
        message_tracker = Mock()
        ONG_TEL_NUMBER = "12354"
        sms_content = "test message"
        with patch.object(SMSClient, "send_sms") as mock_send_sms:
            helper.broadcast_message([], sms_content, ONG_TEL_NUMBER, ["03312345678"], message_tracker, "261")
            mock_send_sms.assert_called_with(ONG_TEL_NUMBER, "2613312345678", sms_content, MSG_TYPE_USER_MSG)
            helper.broadcast_message([], sms_content, ONG_TEL_NUMBER, ["03312345678"], message_tracker)
            mock_send_sms.assert_called_with(ONG_TEL_NUMBER, "03312345678", sms_content, MSG_TYPE_USER_MSG)


class TestPreviewCreator(unittest.TestCase):
    def test_should_create_basic_fields_in_preview(self):
        field = TextField(name="naam", code="nam", label="What's in a name?",
                          instruction="please write more tests")
        preview = helper.get_preview_for_field(field)
        self.assertEquals("What's in a name?", preview["description"])
        self.assertEquals("nam", preview["code"])
        self.assertEquals("text", preview["type"])
        self.assertEquals("please write more tests", preview["instruction"])


    def test_should_add_constraint_text_for_text_field_with_min(self):
        constraints = [TextLengthConstraint(min=10)]
        field = TextField(name="What's in a name?", code="nam", label="naam", constraints=constraints)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("Minimum 10 characters", preview["constraints"])

    def test_should_add_constraint_text_for_text_field_with_max(self):
        constraints = [TextLengthConstraint(max=100)]
        field = TextField(name="What's in a name?", code="nam", label="naam", constraints=constraints)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("Upto 100 characters", preview["constraints"])

    def test_should_add_constraint_text_for_text_field_with_max_and_min(self):
        constraints = [TextLengthConstraint(min=10, max=100)]
        field = TextField(name="What's in a name?", code="nam", label="naam", constraints=constraints)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("Between 10 -- 100 characters", preview["constraints"])

    def test_should_add_constraint_text_for_text_field_without_constraint(self):
        field = TextField(name="What's in a name?", code="nam", label="naam")
        preview = helper.get_preview_for_field(field)
        self.assertEqual("", preview["constraints"])


    def test_should_add_constraint_text_for_numeric_field_with_min(self):
        constraint = NumericRangeConstraint(min=10)
        field = IntegerField(name="What's in the age?", code="nam", label="naam", constraints=[constraint])
        preview = helper.get_preview_for_field(field)
        self.assertEqual("Minimum 10", preview["constraints"])
        self.assertEqual("integer", preview["type"])

    def test_should_add_constraint_text_for_numeric_field_with_max(self):
        constraint = NumericRangeConstraint(max=100)
        field = IntegerField(name="What's in the age?", code="nam", label="naam", constraints=[constraint])
        preview = helper.get_preview_for_field(field)
        self.assertEqual("Upto 100", preview["constraints"])

    def test_should_add_constraint_text_for_numeric_field_with_max_and_min(self):
        constraint = NumericRangeConstraint(min=10, max=100)
        field = IntegerField(name="What's in the age?", code="nam", label="naam", constraints=[constraint])
        preview = helper.get_preview_for_field(field)
        self.assertEqual("10 -- 100", preview["constraints"])

    def test_should_add_constraint_text_for_numeric_field_without_constraint(self):
        field = IntegerField(name="What's in the age?", code="nam", label="naam", )
        preview = helper.get_preview_for_field(field)
        self.assertEqual("", preview["constraints"])

    def test_should_return_choices(self):
        field = SelectField(name="What's the color?", code="nam", label="naam", options=[("Red", "a"), ("Green", "b"), ("Blue", "c")])
        preview = helper.get_preview_for_field(field)
        self.assertEqual("select1", preview["type"])
        self.assertEqual([("Red", "a"), ("Green", "b"), ("Blue", "c")], preview["constraints"])

    def test_should_return_choices_type_as_select(self):
        field = SelectField(name="What's the color?", code="nam", label="naam",
                            options=[("Red", "a"), ("Green", "b"), ("Blue", "c")], single_select_flag=False)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("select", preview["type"])

    def test_should_return_date_format(self):
        field = DateField(name="What is the date?", code="dat", label="naam",  date_format="dd/mm/yyyy")
        preview = helper.get_preview_for_field(field)
        self.assertEqual("dd/mm/yyyy", preview["constraints"])

    def test_should_return_geocode_format(self):
        field = GeoCodeField(name="What is the place?", code="dat", label="naam")
        preview = helper.get_preview_for_field(field)
        self.assertEqual("xx.xxxx yy.yyyy", preview["constraints"])

    def test_should_delete_a_datasender_from_associated_projects(self):
        entity_ids = ['rep1', 'rep2']
        with patch("datawinners.project.models.Project") as mock_project_class:
            mock_project = Mock(spec=Project)
            mock_project_class.get.return_value = mock_project
            with patch("datawinners.project.models.get_all_projects") as all_projects:
                all_projects.return_value = [{'value': {'_id': 1}}]
                dbm = Mock()
                dbm.database.return_value = ''

                delete_datasenders_from_project(dbm, entity_ids)

                self.assertEqual(mock_project.delete_datasender.call_count, 2)
