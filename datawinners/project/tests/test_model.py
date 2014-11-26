# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datetime import date
import unittest
from django.utils.unittest.case import SkipTest
from datawinners.project.couch_view_helper import get_all_projects
from mangrove.datastore.documents import FormModelDocument

from mock import Mock, patch

from mangrove.datastore.cache_manager import get_cache_manager
from mangrove.form_model.project import Project
from mangrove.utils.test_utils.database_utils import uniq
from mangrove.bootstrap import initializer
from datawinners.main.utils import create_views
from datawinners.project.models import get_simple_project_names
from mangrove.datastore.database import DatabaseManager, get_db_manager, _delete_db_and_remove_db_manager
from mangrove.datastore.entity import Entity
from mangrove.form_model.field import TextField, UniqueIdField
from mangrove.form_model.form_model import FormModel, REPORTER
from mangrove.form_model.validation import TextLengthConstraint


project1_name = uniq('Test1')
project2_name = uniq('Test2')

class TestProjectModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        FormModelDocument.registered_functions=[]
        cls.db_name = uniq('mangrove-test')
        cls.manager = get_db_manager('http://localhost:5984/', cls.db_name)
        initializer._create_views(cls.manager)
        create_views(cls.manager)
        question1 = UniqueIdField(unique_id_type='clinic',name="entity_question", code="ID", label="What is associated entity")
        question2 = TextField(name="question1_Name", code="Q1", label="What is your name",
            defaultValue="some default value",
            constraints=[TextLengthConstraint(5, 10)])
        cls.project1 = Project(dbm=cls.manager, name=project1_name, goals="Testing",
                                 devices=['web'], form_code="abc",
                                 fields=[question1, question2])
        cls.project1_id = cls.project1.save()
        cls.project2 = Project(dbm=cls.manager, name=project2_name, goals="Testing",
                                 devices=['web'], form_code="def",
                                 fields=[question1, question2])
        cls.project2_id = cls.project2.save()



    @classmethod
    def tearDownClass(cls):
        _delete_db_and_remove_db_manager(cls.manager)
        get_cache_manager().flush_all()

    def test_get_associated_data_senders(self):
        entity = Entity(self.manager, entity_type=["reporter"], short_code="rep1")
        entity_id = entity.save()
        project = Project(dbm=self.manager, name="TestDS", goals="Testing",
                                  devices=['web'], form_code="ds_form",
                                  fields=[])
        project.data_senders = ["rep1"]
        project.save()
        result = project.get_associated_datasenders(self.manager)

        self.assertEquals(result[0].short_code, entity.short_code)
        self.assertEquals(result[0].id, entity_id)

    def test_get_all_projects(self):
        projects = get_all_projects(self.manager)
        self.assertEquals(len(projects), 2)

    def test_get_all_projects_names(self):
        projects_names = [project['name'] for project in get_simple_project_names(self.manager)]
        self.assertTrue(project1_name in projects_names)
        self.assertTrue(project2_name in projects_names)

    def test_get_one_project(self):
        self.assertEquals(Project.get(self.manager, self.project1_id).id, self.project1_id)

    def test_should_update_project(self):
        self.project1 = Project.get(self.manager, self.project1_id)
        self.project1.update(dict(name=project1_name, devices=['web', 'sms'], goals="New goals"))
        project1_id= self.project1.save()

        project = Project.get(self.manager, project1_id)
        self.assertEquals(project.name, project1_name)
        self.assertEquals(project.goals, 'New goals')
        self.assertEquals(project.devices, ['web', 'sms'])

    def test_project_name_should_be_unique(self):
        questionnaire = Project(dbm=self.manager, name=project2_name, goals="Testing",
                            devices=['web'], form_code="name_form",
                            fields=[])
        with self.assertRaises(Exception) as cm:
            questionnaire.save()
        the_exception = cm.exception
        self.assertEqual(the_exception.message, "Questionnaire with Name = '%s' already exists."%project2_name)

    def test_project_name_should_be_case_insensitively_unique(self):
        questionnaire = Project(self.manager,name=project2_name.upper(), goals="Testing", devices=['web'])
        with self.assertRaises(Exception) as cm:
            questionnaire.save()
        the_exception = cm.exception
        self.assertEqual(the_exception.message, "Questionnaire with Name = '%s' already exists."%project2_name.upper())

    def test_should_check_for_unique_name_while_update_project(self):
        self.project1.update(dict(name=project2_name, devices=['web', 'sms'], goals="New goals"))
        with self.assertRaises(Exception) as cm:
            self.project1.save()
        the_exception = cm.exception
        self.assertEqual(the_exception.message, "Questionnaire with Name = '%s' already exists."%project2_name)


    def test_get_deadline_day(self):
        reminder_and_deadline_for_month = {
            "reminders_enabled": "True",
            "deadline_month": "5",
            "deadline_type": "current",
            "frequency_enabled": "True",
            "has_deadline": "True",
            "frequency_period": "month"
        }
        project_reminders = Project(self.manager,name="ReminderProject")
        project_reminders.reminder_and_deadline = reminder_and_deadline_for_month
        self.assertEquals(5, project_reminders.get_deadline_day())


    def _create_reporter_entity(self, short_code):
        return Entity(dbm=Mock(spec=DatabaseManager), entity_type=REPORTER, short_code=short_code)

    @SkipTest
    def test_should_return_data_senders_without_submissions(self):
        reminder_and_deadline_for_month = {
            "reminders_enabled": "True",
            "deadline_month": "5",
            "deadline_type": "current",
            "frequency_enabled": "True",
            "has_deadline": "True",
            "frequency_period": "month"
        }
        questionnaire = Project(self.manager,name="New project")
        questionnaire.reminder_and_deadline = reminder_and_deadline_for_month
        questionnaire.data_senders = ["rep1", "rep2", "rep3", "rep4", "rep5"]
        dbm = Mock(spec=DatabaseManager)

        with patch("mangrove.form_model.project.get_reporters_who_submitted_data_for_frequency_period") as get_reporters_who_submitted_data_for_frequency_period_mock:
            with patch("mangrove.form_model.project.load_data_senders") as load_data_senders_mock:
                load_data_senders_mock.return_value = (
                [{"cols": ["%s" % rep, rep], "short_code": "%s" % rep}  for rep in questionnaire.data_senders], ["short_code", "mobile_number"],
                ["What is DS Unique ID", "What is DS phone number"])
                get_reporters_who_submitted_data_for_frequency_period_mock.return_value = [
                    self._create_reporter_entity("rep1"), self._create_reporter_entity("rep3")]
                frequency_period_mock = Mock()

                data_senders = questionnaire.get_data_senders_without_submissions_for(date(2011, 11, 5), dbm, frequency_period_mock)

        self.assertEqual(3, len(data_senders))
        self.assertIn("rep2", [ds["short_code"] for ds in data_senders])
        self.assertIn("rep4", [ds["short_code"] for ds in data_senders])
        self.assertIn("rep5", [ds["short_code"] for ds in data_senders])

    def test_should_delete_datasender_from_project(self):
        self.project1 = Project.get(self.manager, self.project1_id)
        self.project1.data_senders = ['rep1', 'rep2']
        datasender_to_be_deleted = 'rep1'
        self.project1.delete_datasender(self.manager, datasender_to_be_deleted)
        self.project1 = Project.get(self.manager, self.project1_id)
        expected_data_senders = ['rep2']
        self.assertEqual(self.project1.data_senders, expected_data_senders)


    def test_should_set_project_to_open_survey(self):
        self.change_is_open_survey_value(True)
        project = Project.get(self.manager, self.project1_id)
        self.assertTrue(project.is_open_survey)
        self.assert_is_changed_to_false()

    def assert_is_changed_to_false(self):
        self.change_is_open_survey_value(False)
        project = Project.get(self.manager, self.project1_id)
        self.assertFalse(project.is_open_survey)

    def change_is_open_survey_value(self, value):
        project = Project.get(self.manager, self.project1_id)
        project.is_open_survey = value
        project.save()
