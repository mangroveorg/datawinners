# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
from datawinners.main.utils import create_views
from datawinners.project.models import Project, get_all_projects, get_project
from mangrove.datastore.database import get_db_manager, _delete_db_and_remove_db_manager
from mangrove.errors.MangroveException import DataObjectAlreadyExists


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

    def tearDown(self):
        _delete_db_and_remove_db_manager(self.dbm)

    def test_get_all_projects(self):
        projects = get_all_projects(self.dbm)
        self.assertEquals(len(projects), 2)

    def test_get_one_project(self):
        self.assertEquals(get_project(self.project1_id, self.dbm)['_id'], self.project1_id)

    def test_should_update_project(self):
        self.project1.update(self.dbm, dict(name='Test1', devices=['web', 'sms'], goals="New goals"))
        self.project1.save(self.dbm)
        self.assertEquals(self.project1.name, 'Test1')
        self.assertEquals(self.project1.goals, 'New goals')
        self.assertEquals(self.project1.devices, ['web', 'sms'])

    def test_project_name_should_be_unique(self):
        project = Project(name="Test2", goals="Testing", project_type="Survey", entity_type="Clinic", devices=['web'])
        with self.assertRaises(DataObjectAlreadyExists):
            project.save(self.dbm)

    def test_should_check_for_unique_name_while_update_project(self):
        self.project1.update(self.dbm, dict(name='Test2', devices=['web', 'sms'], goals="New goals"))
        with self.assertRaises(DataObjectAlreadyExists):
            self.project1.save(self.dbm)
