import unittest
from mock import patch
from datawinners.project.forms import ProjectProfile


class TestProjectProfile(unittest.TestCase):
    def setUp(self):
        self.entity_patcher = patch('datawinners.project.forms.get_all_entity_types')
        self.entity_module = self.entity_patcher.start()

    def tearDown(self):
        self.entity_patcher.stop()

    def test_creates_project_profile_form(self):
        self.entity_module.return_value = ['Reporter']
        base_form = {'name': 'Test Project', 'goals': 'Test Goals', 'project_type': 'survey', 'entity_type': 'Reporter',
                   'devices': ['sms']
        }
        form = ProjectProfile(base_form)
        self.assertTrue(form.is_valid())
        self.assertEquals(form.cleaned_data['name'], 'Test Project')
        self.assertEquals(form.cleaned_data['goals'], 'Test Goals')
        self.assertEquals(form.cleaned_data['project_type'], 'survey')
        self.assertEquals(form.cleaned_data['entity_type'], 'Reporter')
        self.assertEquals(form.cleaned_data['devices'], ['sms'])

    def test_field_goals_not_required(self):
        self.entity_module.return_value = ['Reporter']
        base_form = {'name': 'Test Project', 'project_type': 'survey', 'entity_type': 'Reporter',
                   'devices': ['sms']
        }
        form = ProjectProfile(base_form)
        assert form.is_valid()
