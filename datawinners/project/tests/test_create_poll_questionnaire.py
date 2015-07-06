from unittest import TestCase

from django.contrib.auth.models import User
from mock import MagicMock, patch

from datawinners.project.create_poll import _construct_questionnaire
from datawinners.project.views.poll_views import _is_same_questionnaire
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.project import Project


class TestCreatePoll(TestCase):

    def test_should_construct_questionnaire(self):
        project_name = 'test_poll'
        days_active = 3
        question = "What poll questionnaire?"
        request = MagicMock()

        request.user = MagicMock(spec=User)

        request.POST = {
                    'poll_name': project_name,
                    'active_days': days_active,
                    'question': question,
                    'end_date': "2015-4-28T9:45:31"
                }

        manager = MagicMock(spec=DatabaseManager)
        questionnaire_code = 'poll_'

        with patch('datawinners.project.create_poll.get_database_manager') as get_database_manager_mock:
            with patch('datawinners.project.create_poll.helper.generate_questionnaire_code') as generate_questionnaire_code_mock:
                generate_questionnaire_code_mock.return_value = questionnaire_code
                get_database_manager_mock.return_value = manager
                manager, questionnaire = _construct_questionnaire(request)
                self.assertEquals(questionnaire.name, project_name)
                self.assertIn(questionnaire_code, questionnaire.form_code)


    def test_should_validate_when_current_questionnaire_is_active_and_trying_to_activate_the_same_questionnaire(self):
        is_active = True
        questionnaire = MagicMock(spec=Project)
        questionnaire.id = 'current_active_questionnaire_id'
        question_id_active = 'current_active_questionnaire_id'

        is_active = _is_same_questionnaire(question_id_active, questionnaire)

        self.assertEquals(True, is_active)

    def test_should_validate_when_current_questionnaire_is_active_and_trying_to_activate_another_questionnaire(self):
        is_active = False
        questionnaire = MagicMock(spec=Project)
        questionnaire.id = 'active_questionnaire_id'
        question_id_active = 'current_active_questionnaire_id'

        is_active = _is_same_questionnaire(question_id_active, questionnaire)

        self.assertEquals(False, is_active)






