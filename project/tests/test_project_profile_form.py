import unittest
from datawinners.project.forms import ProjectProfile


class TestProjectProfile(unittest.TestCase):

    def test_creates_project_profile_form(self):
        base_form = {'name': 'Test Project', 'goals': 'Test Goals', 'project_type': 'survey', 'entity_type': 'Reporter',
                     'activity_report': 'yes',
                     'devices': ['sms'], 'sender_group': 'open', 'frequency_enabled':'True', 'language':'en'
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
                     'devices': ['sms'], 'activity_report': 'no', 'sender_group': 'open', 'frequency_enabled':'False', 'language':'en'
        }
        form = ProjectProfile(data=base_form, entity_list=[['Reporter']])
        assert form.is_valid()
