import unittest
from couchdb.client import View, Row
from mock import patch, Mock
from datawinners.entity.subjects import load_subject_type_with_projects, get_subjects_count
from mangrove.datastore.database import DatabaseManager


class TestSubjects(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.manager = Mock(DatabaseManager)
        cls.manager.view = Mock(View)

    def test_should_load_subject_type_with_project_names_sorted(self):
        self.manager.view.projects_by_subject_type = Mock(return_value=[Row({'key':'clinic','value':'acc'}),Row({'key':'clinic','value':'abc'})])
        with patch("datawinners.entity.subjects.get_unique_id_types") as get_entity_types:
            get_entity_types.return_value = ["clinic","waterpoint"]
            projects = load_subject_type_with_projects(self.manager)
            self.assertEqual(["abc","acc"], projects['clinic'])

    def test_should_get_count_of_registered_subjects(self):
        self.manager.view.count_non_voided_entities_by_type = Mock(return_value=[Row({'key':['clinic'],'value':10})])
        subject_count = get_subjects_count(self.manager)
        self.assertEquals(subject_count.get('clinic'),10)

    def test_should_not_include_reporter_in_subject_types_list(self):
        self.manager.view.projects_by_subject_type = Mock(return_value=[Row({'key':'clinic','value':'acc'}),Row({'key':'reporter','value':'tester'})])
        with patch("datawinners.entity.subjects.get_unique_id_types") as get_entity_types:
            get_entity_types.return_value = ["clinic"]
            result = load_subject_type_with_projects(self.manager)
            self.assertEquals(result.__len__(),1)
            self.assertDictEqual({'clinic':['acc']},result)
            self.assertNotIn('reporter',result.keys())
