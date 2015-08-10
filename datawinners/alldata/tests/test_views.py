from unittest import TestCase

from django.contrib.auth.models import User
from mock import Mock, patch

from mangrove.datastore.database import DatabaseManager
from datawinners.accountmanagement.models import NGOUserProfile
from datawinners.alldata.views import  get_project_info, index, get_project_list
from mangrove.form_model.project import Project


class TestViews(TestCase):
    def test_get_correct_web_submission_link(self):
        request = Mock()
        request.user = Mock(spec = User)
        manager = Mock(spec = DatabaseManager)
        manager.database = dict()
        raw_project = dict(_id = "pid", devices = ["sms", "web"],
                                        name = "Project Name",
                                        created = "2012-05-23T02:57:09.788294+00:00")

        project = Project(dbm=manager, name="Project Name")

        profile = Mock(spec = NGOUserProfile)

        questionnaire = Mock()
        questionnaire.form_code = "q01"

        with patch("datawinners.project.models.Project.get") as get_project:
            get_project.return_value = project
            with patch.object(DatabaseManager, "get") as db_manager:
                db_manager.return_value = questionnaire
                with patch("django.contrib.auth.models.User.get_profile") as get_profile:
                    get_profile.return_value = profile
                    profile.reporter = False
                    project_info = get_project_info(manager, raw_project)
                    self.assertEqual(project_info["web_submission_link"], "/project/testquestionnaire/pid/")

    def test_get_submission_link_if_poll_questionnaire(self):
        request = Mock()
        request.user = Mock(spec = User)
        manager = Mock(spec = DatabaseManager)
        manager.database = dict()
        raw_project = dict(_id = "pid", devices = ["sms", "web"],
                                        name = "Project Name",
                                        created = "2012-05-23T02:57:09.788294+00:00",
                                        is_poll=True, form_code="q01")

        project = Project(dbm=manager, name="Project Name", is_poll=True, form_code="q01")
        profile = Mock(spec = NGOUserProfile)

        questionnaire = Mock()
        questionnaire.form_code = "q01"

        with patch.object(DatabaseManager, "get") as db_manager:
            db_manager.return_value = questionnaire
            with patch("django.contrib.auth.models.User.get_profile") as get_profile:
                get_profile.return_value = profile
                profile.reporter = False
                project_info = get_project_info(manager, raw_project)
                self.assertEqual(project_info["link"], "/project/pid/results/q01/")

    @patch('datawinners.alldata.views.get_database_manager')    
    @patch('datawinners.alldata.views.get_all_project_for_user')            
    def test_should_get_project_list_for_project_manager(self, mock_get_all_project_for_user, mock_get_database_manager):
        request = Mock()
        request.user = Mock(spec = User)
        manager = Mock(spec = DatabaseManager)
        manager.database = dict()
        mock_get_database_manager.return_value = manager 
        raw_project = dict(_id = "pid", devices = ["sms", "web"],
                                        name = "Project Name",
                                        is_project_manager = True,
                                        created = "2012-05-23T02:57:09.788294+00:00",
                                        is_poll=True, form_code="q01")
        mock_get_all_project_for_user.return_value = [raw_project]
        project_list = get_project_list(request)
        self.assertEqual(project_list[0].get('is_project_manager'),True)
        self.assertEqual(project_list[0].get('name'),'Project Name')
        self.assertEqual(project_list[0].get('is_poll'),True)
