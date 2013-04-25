from unittest.case import TestCase, SkipTest
from django.contrib.gis.utils.geoip import GeoIP
from django.http import HttpRequest, HttpResponse
from django_countries.fields import Country
from django_digest import HttpDigestAuthenticator
from mock import Mock, patch
from datawinners.xforms.views import formList, xform, restrict_request_country

class TestXFormsViews(TestCase):
    def setUp(self):
        self.request = Mock(spec=HttpRequest)
        self.request.user = Mock()

            #### All The Skipped Tests Cannot be tested because of decorators need to find a way
    @SkipTest
    def test_should_authenticate_with_digest_authentication(self):
        with patch.object(HttpDigestAuthenticator, 'authenticate') as mock_authenticate:
            with patch("datawinners.xforms.views.get_all_project_for_user") as mock_get_all_projects:
                mock_get_all_projects.return_value = []
                with patch("datawinners.xforms.views.list_all_forms"):
                    formList(self.request)
                    self.assertEquals(mock_authenticate.call_count, 1)

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
                with patch.object('HttpDigestAuthenticator', 'authenticate') as mock_authenticate:
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

    def test_should_allow_request_from_country_other_than_of_organization(self):
        request = Mock(spec=HttpRequest)
        request.user = Mock()
        request.META = {'REMOTE_ADDR': "someIp"}
        with patch('datawinners.xforms.views.Organization') as organization_mock:
            mock_organization = Mock()
            mock_organization.country = Country('IN')
            objects_mock = Mock()
            objects_mock.get.return_value = mock_organization
            organization_mock.objects = objects_mock
            with patch.object(GeoIP, 'country_code') as geo_ip_mock:
                geo_ip_mock.return_value = Country('MG')
                self.assertEquals(dummy_form_list(request).status_code, 200)

    def test_should_allow_request_from_country_of_organization(self):
        request = Mock(spec=HttpRequest)
        request.user = Mock()
        request.META = {'REMOTE_ADDR': "someIp"}
        with patch('datawinners.xforms.views.Organization') as organization_mock:
            mock_organization = Mock()
            country = Country('IN')
            mock_organization.country = country
            objects_mock = Mock()
            objects_mock.get.return_value = mock_organization
            organization_mock.objects = objects_mock
            with patch.object(GeoIP, 'country_code') as geo_ip_mock:
                geo_ip_mock.return_value = country
                self.assertEquals(dummy_form_list(request).status_code, 200)


@restrict_request_country
def dummy_form_list(request):
    return HttpResponse()




