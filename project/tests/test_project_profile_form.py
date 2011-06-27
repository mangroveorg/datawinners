import unittest
from datawinners.project.forms import ProjectProfile


class TestProjectProfile(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_creates_project_profile_form(self):
        base_form = {'name': 'Test Project', 'goals': 'Test Goals', 'project_type': 'survey', 'entity_type': 'Reporter', 'activity_report':'activity_report',
                     'devices': ['sms']
        }
        form = ProjectProfile(data=base_form, entity_list=[['Reporter']])
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEquals(form.cleaned_data['name'], 'Test Project')
        self.assertEquals(form.cleaned_data['goals'], 'Test Goals')
        self.assertEquals(form.cleaned_data['project_type'], 'survey')
        self.assertEquals(form.cleaned_data['entity_type'], 'reporter')
        self.assertEquals(form.cleaned_data['devices'], ['sms'])

    def test_field_goals_not_required(self):
        base_form = {'name': 'Test Project', 'project_type': 'survey', 'entity_type': 'Reporter',
                     'devices': ['sms'], 'activity_report':'activity_report'
        }
        form = ProjectProfile(data=base_form, entity_list=[['Reporter']])
        assert form.is_valid()
