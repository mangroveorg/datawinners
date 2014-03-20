# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datetime import date
import unittest

from mock import Mock, patch

from mangrove.datastore.cache_manager import get_cache_manager
from mangrove.utils.test_utils.database_utils import uniq
from mangrove.bootstrap import initializer
from datawinners.main.utils import create_views
from datawinners.project.models import Project, get_all_projects, get_all_project_names
from mangrove.datastore.database import DatabaseManager, get_db_manager, _delete_db_and_remove_db_manager
from mangrove.datastore.documents import attributes
from mangrove.datastore.entity import Entity
from mangrove.form_model.field import TextField, UniqueIdField
from mangrove.form_model.form_model import FormModel, REPORTER
from mangrove.form_model.validation import TextLengthConstraint


project1_name = uniq('Test1')
project2_name = uniq('Test2')

class TestProjectModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_name = uniq('mangrove-test')
        cls.manager = get_db_manager('http://localhost:5984/', cls.db_name)
        initializer._create_views(cls.manager)
        create_views(cls.manager)
        cls.project1 = Project(name=project1_name, goals="Testing", entity_type="Clinic", devices=['web'])
        cls.project1_id = cls.project1.save(cls.manager)
        cls.project2 = Project(name=project2_name, goals="Testing", entity_type="Clinic", devices=['web'])
        cls.project2_id = cls.project2.save(cls.manager)

        cls._create_form_model_for_project(cls.project1)

    @classmethod
    def _create_form_model_for_project(cls, project):
        question1 = UniqueIdField(unique_id_type='clinic',name="entity_question", code="ID", label="What is associated entity")
        question2 = TextField(name="question1_Name", code="Q1", label="What is your name",
            defaultValue="some default value",
            constraints=[TextLengthConstraint(5, 10)])
        cls.form_model = FormModel(cls.manager, name=cls.project1.name, form_code="abc",
            fields=[question1, question2])
        qid = cls.form_model.save()
        project.qid = qid
        project.save(cls.manager)

    @classmethod
    def tearDownClass(cls):
        _delete_db_and_remove_db_manager(cls.manager)
        get_cache_manager().flush_all()

    def test_get_associated_data_senders(self):
        entity = Entity(self.manager,entity_type=["reporter"], short_code="rep1")
        entity_id = entity.save()
        project = Project(name="TestDS", goals="Testing", devices=['web'])
        project.data_senders = ["rep1"]
        project.save(self.manager)

        result = project.get_associated_datasenders(self.manager)

        self.assertEquals(result[0].short_code, entity.short_code)
        self.assertEquals(result[0].id, entity_id)

    def test_get_all_projects(self):
        projects = get_all_projects(self.manager)
        self.assertEquals(len(projects), 2)

    def test_get_all_projects_names(self):
        projects_names = [project['name'] for project in get_all_project_names(self.manager)]
        self.assertTrue(project1_name.lower() in projects_names)
        self.assertTrue(project2_name.lower() in projects_names)

    def test_get_one_project(self):
        self.assertEquals(Project.load(self.manager.database, self.project1_id)['_id'], self.project1_id)

    def test_should_update_project(self):
        self.project1 = Project.load(self.manager.database, self.project1_id)
        self.project1.update(dict(name=project1_name, devices=['web', 'sms'], goals="New goals"))
        self.project1.save(self.manager)
        self.assertEquals(self.project1.name, project1_name.lower())
        self.assertEquals(self.project1.goals, 'New goals')
        self.assertEquals(self.project1.devices, ['web', 'sms'])

    def test_project_name_should_be_unique(self):
        project = Project(name=project2_name, goals="Testing", entity_type="Clinic", devices=['web'])
        with self.assertRaises(Exception) as cm:
            project.save(self.manager)
        the_exception = cm.exception
        self.assertEqual(the_exception.message, "Questionnaire with Name = '%s' already exists."%project2_name.lower())

    def test_project_name_should_be_case_insensitively_unique(self):
        project = Project(name=project2_name.upper(), goals="Testing", entity_type="Clinic", devices=['web'])
        with self.assertRaises(Exception) as cm:
            project.save(self.manager)
        the_exception = cm.exception
        self.assertEqual(the_exception.message, "Questionnaire with Name = '%s' already exists."%project2_name.lower())

    def test_should_check_for_unique_name_while_update_project(self):
        self.project1.update(dict(name=project2_name, devices=['web', 'sms'], goals="New goals"))
        with self.assertRaises(Exception) as cm:
            self.project1.save(self.manager)
        the_exception = cm.exception
        self.assertEqual(the_exception.message, "Questionnaire with Name = '%s' already exists."%project2_name.lower())


    def test_get_deadline_day(self):
        reminder_and_deadline_for_month = {
            "reminders_enabled": "True",
            "deadline_month": "5",
            "deadline_type": "current",
            "frequency_enabled": "True",
            "has_deadline": "True",
            "frequency_period": "month"
        }
        project_reminders = Project(name="ReminderProject")
        project_reminders.reminder_and_deadline = reminder_and_deadline_for_month
        self.assertEquals(5, project_reminders.get_deadline_day())


    def _create_reporter_entity(self, short_code):
        return Entity(dbm=Mock(spec=DatabaseManager), entity_type=REPORTER, short_code=short_code)


    def test_should_return_data_senders_without_submissions(self):
        reminder_and_deadline_for_month = {
            "reminders_enabled": "True",
            "deadline_month": "5",
            "deadline_type": "current",
            "frequency_enabled": "True",
            "has_deadline": "True",
            "frequency_period": "month"
        }
        project = Project()
        project.reminder_and_deadline = reminder_and_deadline_for_month
        project.data_senders = ["rep1", "rep2", "rep3", "rep4", "rep5"]
        dbm = Mock(spec=DatabaseManager)

        with patch("datawinners.project.models.get_reporters_who_submitted_data_for_frequency_period") as get_reporters_who_submitted_data_for_frequency_period_mock:
            with patch("datawinners.project.models.load_data_senders") as load_data_senders_mock:
                load_data_senders_mock.return_value = (
                [{"cols": ["%s" % rep, rep], "short_code": "%s" % rep}  for rep in project.data_senders], ["short_code", "mobile_number"],
                ["What is DS Unique ID", "What is DS phone number"])
                get_reporters_who_submitted_data_for_frequency_period_mock.return_value = [
                    self._create_reporter_entity("rep1"), self._create_reporter_entity("rep3")]

                data_senders = project.get_data_senders_without_submissions_for(date(2011, 11, 5), dbm)

        self.assertEqual(3, len(data_senders))
        self.assertIn("rep2", [ds["short_code"] for ds in data_senders])
        self.assertIn("rep4", [ds["short_code"] for ds in data_senders])
        self.assertIn("rep5", [ds["short_code"] for ds in data_senders])

    def test_should_delete_datasender_from_project(self):
        self.project1 = Project.load(self.manager.database, self.project1_id)
        self.project1.data_senders = ['rep1', 'rep2']
        datasender_to_be_deleted = 'rep1'
        with patch("datawinners.search.datasender_index.update_datasender_index_by_id") as update_datasender_index_by_id:
            update_datasender_index_by_id.return_value = None
            self.project1.delete_datasender(self.manager, datasender_to_be_deleted)
            self.project1 = Project.load(self.manager.database, self.project1_id)
            expected_data_senders = ['rep2']
            self.assertEqual(self.project1.data_senders, expected_data_senders)

