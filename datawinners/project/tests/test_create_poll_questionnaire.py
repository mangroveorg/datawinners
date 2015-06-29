import json
from unittest import TestCase
from django.contrib.auth.models import User
from mock import MagicMock, patch, Mock, PropertyMock
from datawinners.project.create_poll import _construct_questionnaire, _is_project_name_unique
from datawinners.project.views.poll_views import _is_active, _is_same_questionnaire
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


    def test_should_validate_project_name_to_be_unique(self):
        error_message = {}
        name_has_errors = False
        questionnaire = MagicMock(spec=Project)

        questionnaire.is_project_name_unique.return_value = False

        project_name_unique = _is_project_name_unique(error_message, name_has_errors, questionnaire)
        self.assertEquals(project_name_unique, True)

    def test_should_validate_project_name_if_not_unique(self):
        error_message = {}
        name_has_errors = False
        questionnaire = MagicMock(spec=Project)

        questionnaire.is_project_name_unique.return_value = True

        project_name_unique = _is_project_name_unique(error_message, name_has_errors, questionnaire)
        self.assertEquals(project_name_unique, False)

    def test_should_validate_questionnaire_is_active(self):
        questionnaire = MagicMock(spec=Project)
        questionnaire.active = "active"

        is_active = _is_active(questionnaire)

        self.assertEquals(True, is_active)

    def test_should_validate_questionnaire_is_not_active(self):
        questionnaire = MagicMock(spec=Project)
        questionnaire.active = "deactivate"

        is_active = _is_active(questionnaire)

        self.assertEquals(False, is_active)

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






