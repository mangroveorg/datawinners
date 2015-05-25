import json
from unittest import TestCase
from django.contrib.auth.models import User
from mock import MagicMock, patch, Mock, PropertyMock
from datawinners.project.create_poll import create_poll_questionnaire, _construct_questionnaire, _is_project_name_unique
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.project import Project


class TestCreatePoll(TestCase):

    def test_should_create_a_poll_questionnaire(self):
        project_name = 'test_poll'
        days_active = 3
        question = "What poll questionnaire?"
        request = MagicMock()

        request.user = MagicMock(spec=User)

        manager = MagicMock(spec=DatabaseManager)

        questionnaire_code = 'q_code'

        request.POST = {
            'poll_name': project_name,
            'active_days': days_active,
            'question': question,
            'selected_option': '{"option":"broadcast"}'
        }
        selected_option = {"option": "broadcast"}

        questionnaire = MagicMock(spec=Project)
        questionnaire.id = 'some_id'
        questionnaire.form_code = "some_code"

        with patch('datawinners.project.create_poll.get_database_manager') as get_database_manager_mock:
            with patch('datawinners.project.create_poll.helper.generate_questionnaire_code') as generate_questionnaire_code_mock:
                with patch('datawinners.project.create_poll.helper.Project') as project_mock:
                    with patch('datawinners.project.create_poll._construct_questionnaire') as _construct_questionnaire_mock:
                        with patch('datawinners.project.create_poll._is_project_name_unique') as _is_project_name_unique_mock:
                            with patch('datawinners.project.create_poll._create_poll') as _create_poll_mock:
                                project_mock.return_value = questionnaire
                                get_database_manager_mock.return_value = manager
                                _construct_questionnaire_mock.return_value = manager, questionnaire
                                generate_questionnaire_code_mock.return_value = questionnaire_code
                                _is_project_name_unique_mock.return_value = False

                                response = create_poll_questionnaire(request)
                                self.assertDictEqual(json.loads(response.content), {"project_id": "some_id", "success": True, "project_code": "some_code"})

                                _create_poll_mock.assert_called_with(manager, questionnaire, selected_option, question)

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
        questionnaire_code = 'q_code'


        with patch('datawinners.project.create_poll.get_database_manager') as get_database_manager_mock:
            with patch('datawinners.project.create_poll.helper.generate_questionnaire_code') as generate_questionnaire_code_mock:
                generate_questionnaire_code_mock.return_value = questionnaire_code
                get_database_manager_mock.return_value = manager
                manager, questionnaire = _construct_questionnaire(request)
                self.assertEquals(questionnaire.name, project_name)
                self.assertEquals(questionnaire.form_code, questionnaire_code)


    def test_should_is_project_name_unique(self):
        error_message = {}
        name_has_errors = False
        questionnaire = MagicMock(spec=Project)

        questionnaire.is_project_name_unique.return_value = False

        project_name_unique = _is_project_name_unique(error_message, name_has_errors, questionnaire)
        self.assertEquals(project_name_unique, True)

    def test_should_is_project_name_not_unique(self):
        error_message = {}
        name_has_errors = False
        questionnaire = MagicMock(spec=Project)

        questionnaire.is_project_name_unique.return_value = True

        project_name_unique = _is_project_name_unique(error_message, name_has_errors, questionnaire)
        self.assertEquals(project_name_unique, False)










