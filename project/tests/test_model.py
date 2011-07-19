# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
from mock import Mock, patch
from datawinners.main.utils import create_views
from datawinners.project.models import Project, get_all_projects, get_project, ProjectState
from mangrove.datastore.database import get_db_manager, _delete_db_and_remove_db_manager, DatabaseManager
from mangrove.datastore.datadict import DataDictType
from mangrove.datastore.documents import attributes
from mangrove.errors.MangroveException import DataObjectAlreadyExists
from mangrove.form_model.field import TextField
from mangrove.form_model.form_model import FormModel
from mangrove.form_model.validation import TextConstraint


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

    def _create_form_model_for_project(self,project):
        ddtype = DataDictType(self.dbm, name='Default String Datadict Type', slug='string_default',
                              primitive_type='string')
        question1 = TextField(name="entity_question", code="ID", label="What is associated entity",
                              language="eng", entity_question_flag=True, ddtype=ddtype)
        question2 = TextField(name="question1_Name", code="Q1", label="What is your name",
                              defaultValue="some default value", language="eng", length=TextConstraint(5, 10),
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
        self.assertEquals(ProjectState.ACTIVE,self.project1.state)

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

        self.assertEqual( ProjectState.INACTIVE, project.state)

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

        self.assertEqual( ProjectState.TEST, project.state)


