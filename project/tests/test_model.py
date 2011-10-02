# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datetime import date

import unittest
from mock import Mock, patch
from datawinners.main.utils import create_views
from datawinners.project.models import Project, get_all_projects, get_project, ProjectState
from mangrove.datastore.database import get_db_manager, _delete_db_and_remove_db_manager, DatabaseManager
from mangrove.datastore.datadict import DataDictType
from mangrove.datastore.documents import attributes
from mangrove.datastore.entity import Entity
from mangrove.errors.MangroveException import DataObjectAlreadyExists
from mangrove.form_model.field import TextField
from mangrove.form_model.form_model import FormModel, REPORTER
from mangrove.form_model.validation import TextLengthConstraint


class TestProjectModel(unittest.TestCase):
    def setUp(self):
        self.dbm = get_db_manager(database='mangrove-test')
        create_views(self.dbm)
        self.project1 = Project(name="Test1", goals="Testing", project_type="Survey", entity_type="Clinic",
                                devices=['web'])
        self.project1_id = self.project1.save(self.dbm)
        self.project2 = Project(name="Test2", goals="Testing", project_type="Survey", entity_type="Clinic",
                                devices=['web'])
        self.project2_id = self.project2.save(self.dbm)

        self._create_form_model_for_project(self.project1)

    def tearDown(self):
        _delete_db_and_remove_db_manager(self.dbm)

    def test_get_all_projects(self):
        projects = get_all_projects(self.dbm)
        self.assertEquals(len(projects), 2)

    def test_get_one_project(self):
        self.assertEquals(get_project(self.project1_id, self.dbm)['_id'], self.project1_id)

    def test_should_update_project(self):
        self.project1.update(dict(name='Test1', devices=['web', 'sms'], goals="New goals"))
        self.project1.save(self.dbm)
        self.assertEquals(self.project1.name, 'test1')
        self.assertEquals(self.project1.goals, 'New goals')
        self.assertEquals(self.project1.devices, ['web', 'sms'])

    def test_project_name_should_be_unique(self):
        project = Project(name="Test2", goals="Testing", project_type="Survey", entity_type="Clinic", devices=['web'])
        with self.assertRaises(DataObjectAlreadyExists):
            project.save(self.dbm)

    def test_project_name_should_be_case_insensitively_unique(self):
        project = Project(name="tEsT2", goals="Testing", project_type="Survey", entity_type="Clinic", devices=['web'])
        with self.assertRaises(DataObjectAlreadyExists):
            project.save(self.dbm)

    def test_should_check_for_unique_name_while_update_project(self):
        self.project1.update(dict(name='Test2', devices=['web', 'sms'], goals="New goals"))
        with self.assertRaises(DataObjectAlreadyExists):
            self.project1.save(self.dbm)

    def _create_form_model_for_project(self, project):
        ddtype = DataDictType(self.dbm, name='Default String Datadict Type', slug='string_default',
                              primitive_type='string')
        question1 = TextField(name="entity_question", code="ID", label="What is associated entity",
                              language="eng", entity_question_flag=True, ddtype=ddtype)
        question2 = TextField(name="question1_Name", code="Q1", label="What is your name",
                              defaultValue="some default value", language="eng",
                              constraints=[TextLengthConstraint(5, 10)],
                              ddtype=ddtype)
        self.form_model = FormModel(self.dbm, name=self.project1.name, form_code="abc", fields=[question1, question2],
                                    entity_type=["Clinic"], state=attributes.INACTIVE_STATE)
        qid = self.form_model.save()
        project.qid = qid
        project.save(self.dbm)

    def test_should_update_questionnaire(self):
        self.project1.name = "New Name"
        self.project1.update_questionnaire(self.dbm)
        form_model = self.dbm.get(self.project1.qid, FormModel)
        self.assertEqual("New Name", form_model.name)

    def test_should_activate_form_on_project_activate(self):
        form_model = self.dbm.get(self.project1.qid, FormModel)
        self.assertFalse(form_model.is_active())
        self.project1.activate(self.dbm)
        form_model = self.dbm.get(self.project1.qid, FormModel)
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
        project_reminders = Project(name="ReminderProject", reminder_and_deadline=reminder_and_deadline_for_month)
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
        project = Project(reminder_and_deadline=reminder_and_deadline_for_month)
        project.data_senders = ["rep1", "rep2", "rep3", "rep4", "rep5"]
        dbm = Mock(spec=DatabaseManager)

        with patch(
            "datawinners.project.models.get_reporters_who_submitted_data_for_frequency_period") as get_reporters_who_submitted_data_for_frequency_period_mock:
            with patch("datawinners.project.models.load_all_subjects_of_type") as load_all_subjects_of_type_mock:
                load_all_subjects_of_type_mock.return_value = [{"short_name": "rep%s" % i, "mobile_number": i}  for i in
                                                                                                                range(
                                                                                                                    10)]
                get_reporters_who_submitted_data_for_frequency_period_mock.return_value = [
                    self._create_reporter_entity("rep1"), self._create_reporter_entity("rep3")]

                data_senders = project.get_data_senders_without_submissions_for(date(2011, 11, 5), dbm)

        self.assertEqual(3, len(data_senders))
        self.assertIn("rep2", [ds["short_name"]  for ds in data_senders])
        self.assertIn("rep4", [ds["short_name"]  for ds in data_senders])
        self.assertIn("rep5", [ds["short_name"]  for ds in data_senders])







