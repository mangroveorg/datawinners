from unittest.case import TestCase
from mock import Mock, patch
from datawinners.entity.helper import delete_datasender_from_project
from datawinners.project.models import Project

class TestHelper(TestCase):
    def setUp(self):
        self.manager = Mock()
        self.all_projects_patch = patch("datawinners.entity.helper.get_all_projects")
        self.all_projects_mock = self.all_projects_patch.start()
        self.project_DO_patch = patch("datawinners.entity.helper.Project")
        self.project_DO_mock = self.project_DO_patch.start()
        self.associated_project = {'value': {'_id': 'someId'}}
        self.associated_projects = [self.associated_project]
        self.mock_project = Mock(spec=Project)

    def test_should_delete_a_datasender_from_associated_projects(self):
        entity_ids = ['rep1', 'rep2']
        self.all_projects_mock.return_value = self.associated_projects
        self.project_DO_mock.load.return_value = self.mock_project
        delete_datasender_from_project(self.manager, entity_ids)
        self.assertEqual(self.mock_project.delete_datasender.call_count, 2)

    def tearDown(self):
        self.all_projects_patch.stop()

