from unittest.case import TestCase, SkipTest
from mock import Mock, patch
from datawinners.xforms.views import formList, xform

class TestXFormsViews(TestCase):
    def setUp(self):
        self.digest_patcher = patch("datawinners.xforms.views.httpdigest")
        self.digest_mock = self.digest_patcher.start()
        self.digest_mock.return_value = True

    def tearDown(self):
        self.digest_patcher.stop()


    @SkipTest
    def test_should_retrieve_list_of_all_forms(self):
        request = Mock()
        uri = "absolute_uri"
        request.build_absolute_uri.return_value = uri
        project = {'value': {'name': 'name_of_project', 'qid': 'questionnaire_id'}}
        projects = [project]
        form_tuples = [('name_of_project', 'questionnaire_id')]
        with patch("datawinners.xforms.views.get_all_project_for_user") as mock_get_all_projects:
            mock_get_all_projects.return_value = projects
            with patch("datawinners.xforms.views.list_all_forms") as mock_list_all_forms:
                formList(request)
                mock_list_all_forms.assert_called_once_with(form_tuples, uri)

    @SkipTest
    def test_should_retrieve_specific_xform_by_questionnaire_code(self):
        request = Mock()
        questionnaire_code = "someCode"
        dbm = "dbm"
        with patch("datawinners.xforms.views.get_database_manager") as mock_get_dbm:
            mock_get_dbm.return_value = dbm
            with patch("datawinners.xforms.views.xform_for") as mock_xform_for:
                xform(request, questionnaire_code)
                mock_xform_for.assert_called_once_with(mock_get_dbm(), questionnaire_code)


