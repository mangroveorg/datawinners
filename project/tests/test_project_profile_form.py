import unittest
from datawinners.project.forms import ProjectProfile


class TestProjectProfile(unittest.TestCase):

    def test_creates_project_profile_form(self):
        base_form={'name':'Test Project', 'goals':'Test Goals','project_type':'survey','entity_type':'Reporter',
                   'device':['sms']
        }
        form = ProjectProfile(base_form)
        self.assertTrue(form.is_valid())
        self.assertEquals(form.cleaned_data['name'],'Test Project')
        self.assertEquals(form.cleaned_data['goals'],'Test Goals')
        self.assertEquals(form.cleaned_data['project_type'],'survey')
        self.assertEquals(form.cleaned_data['entity_type'],'Reporter')
        self.assertEquals(form.cleaned_data['device'],['sms'])


    def test_field_goals_not_required(self):
        base_form={'name':'Test Project','project_type':'survey','entity_type':'Reporter',
                   'device':['sms']
        }
        form = ProjectProfile(base_form)
        assert form.is_valid()


