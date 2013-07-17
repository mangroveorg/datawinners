# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datetime import date

from mangrove.utils.test_utils.mangrove_test_case import MangroveTestCase
from mock import Mock, patch
from datawinners.main.utils import create_views
from datawinners.project.models import Project, get_all_projects, ProjectState
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.datadict import DataDictType
from mangrove.datastore.documents import attributes
from mangrove.datastore.entity import Entity
from mangrove.form_model.field import TextField
from mangrove.form_model.form_model import FormModel, REPORTER
from mangrove.form_model.validation import TextLengthConstraint


class TestProjectModel(MangroveTestCase):
    def setUp(self):
        MangroveTestCase.setUp(self)
        create_views(self.manager)
        self.project1 = Project(name="Test1", goals="Testing", project_type="Survey", entity_type="Clinic",
            devices=['web'])
        self.project1_id = self.project1.save(self.manager)
        self.project2 = Project(name="Test2", goals="Testing", project_type="Survey", entity_type="Clinic",
            devices=['web'])
        self.project2_id = self.project2.save(self.manager)

        self._create_form_model_for_project(self.project1)

    def tearDown(self):
        MangroveTestCase.tearDown(self)

    def test_get_all_projects(self):
        projects = get_all_projects(self.manager)
        self.assertEquals(len(projects), 2)

    def test_get_one_project(self):
        self.assertEquals(Project.load(self.manager.database, self.project1_id)['_id'], self.project1_id)

    def test_should_update_project(self):
        self.project1.update(dict(name='Test1', devices=['web', 'sms'], goals="New goals"))
        self.project1.save(self.manager)
        self.assertEquals(self.project1.name, 'test1')
        self.assertEquals(self.project1.goals, 'New goals')
        self.assertEquals(self.project1.devices, ['web', 'sms'])

    def test_project_name_should_be_unique(self):
        project = Project(name="Test2", goals="Testing", project_type="Survey", entity_type="Clinic", devices=['web'])
        with self.assertRaises(Exception) as cm:
            project.save(self.manager)
        the_exception = cm.exception
        self.assertEqual(the_exception.message, "Project with Name = 'test2' already exists.")

    def test_project_name_should_be_case_insensitively_unique(self):
        project = Project(name="tEsT2", goals="Testing", project_type="Survey", entity_type="Clinic", devices=['web'])
        with self.assertRaises(Exception) as cm:
            project.save(self.manager)
        the_exception = cm.exception
        self.assertEqual(the_exception.message, "Project with Name = 'test2' already exists.")

    def test_should_check_for_unique_name_while_update_project(self):
        self.project1.update(dict(name='Test2', devices=['web', 'sms'], goals="New goals"))
        with self.assertRaises(Exception) as cm:
            self.project1.save(self.manager)
        the_exception = cm.exception
        self.assertEqual(the_exception.message, "Project with Name = 'test2' already exists.")

    def _create_form_model_for_project(self, project):
        ddtype = DataDictType(self.manager, name='Default String Datadict Type', slug='string_default',
            primitive_type='string')
        question1 = TextField(name="entity_question", code="ID", label="What is associated entity", entity_question_flag=True, ddtype=ddtype)
        question2 = TextField(name="question1_Name", code="Q1", label="What is your name",
            defaultValue="some default value",
            constraints=[TextLengthConstraint(5, 10)],
            ddtype=ddtype)
        self.form_model = FormModel(self.manager, name=self.project1.name, form_code="abc",
            fields=[question1, question2],
            entity_type=["Clinic"], state=attributes.INACTIVE_STATE)
        qid = self.form_model.save()
        project.qid = qid
        project.save(self.manager)

    def test_should_update_questionnaire(self):
        self.project1.name = "New Name"
        self.project1.update_questionnaire(self.manager)
        form_model = self.manager.get(self.project1.qid, FormModel)
        self.assertEqual("New Name", form_model.name)

    def test_should_activate_form_on_project_activate(self):
        form_model = self.manager.get(self.project1.qid, FormModel)
        self.assertFalse(form_model.is_active())
        self.project1.activate(self.manager)
        form_model = self.manager.get(self.project1.qid, FormModel)
        self.assertTrue(form_model.is_active())
        self.assertEquals(ProjectState.ACTIVE, self.project1.state)

    def test_should_deactivate_form_on_project_deactivate(self):
        project = Project(state=ProjectState.ACTIVE)
        dbm = Mock(spec=DatabaseManager)
        form_model_mock = Mock(spec=FormModel)
        dbm.get.return_value = form_model_mock

        with patch("datawinners.project.models.Project.save") as project_save_mock:
            project.deactivate(dbm)

            form_model_mock.deactivate.assert_called_once_with()
            form_model_mock.save.assert_called_once_with()
            project_save_mock.assert_called_once_with(dbm)

        self.assertEqual(ProjectState.INACTIVE, project.state)

    def test_should_set_form_to_test_on_project_set_to_test(self):
        project = Project(state=ProjectState.ACTIVE)
        dbm = Mock(spec=DatabaseManager)
        form_model_mock = Mock(spec=FormModel)
        dbm.get.return_value = form_model_mock

        with patch("datawinners.project.models.Project.save") as project_save_mock:
            project.to_test_mode(dbm)

            form_model_mock.set_test_mode.assert_called_once_with()
            form_model_mock.save.assert_called_once_with()
            project_save_mock.assert_called_once_with(dbm)

        self.assertEqual(ProjectState.TEST, project.state)

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
        self.project1.data_senders = ['rep1', 'rep2']
        datasender_to_be_deleted = 'rep1'
        self.project1.delete_datasender(self.manager, datasender_to_be_deleted)
        self.project1 = Project.load(self.manager.database, self.project1_id)
        expected_data_senders = ['rep2']
        self.assertEqual(self.project1.data_senders, expected_data_senders)









