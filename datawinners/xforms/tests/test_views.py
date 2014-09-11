from unittest.case import TestCase, SkipTest
from django.contrib.gis.utils.geoip import GeoIP
from django.http import HttpRequest, HttpResponse
from django_countries.fields import Country
from django_digest import HttpDigestAuthenticator
from mock import Mock, patch, MagicMock
from datawinners.accountmanagement.models import NGOUserProfile
from datawinners.xforms.views import formList, xform, restrict_request_country, is_authorized_for_questionnaire
from mangrove.form_model.form_model import FormModel


class TestXFormsViews(TestCase):
    def setUp(self):
        self.request = Mock(spec=HttpRequest)
        self.request.user = Mock()

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

    def test_should_return_false_when_datasender_is_not_associated_with_questionnaire(self):
        dbm = MagicMock()
        requested_user = MagicMock()
        user_profile = MagicMock(spec=NGOUserProfile)
        user_profile.reporter_id = 'rep123'
        requested_user.get_profile.return_value = user_profile
        with patch('datawinners.xforms.views.get_form_model_by_code') as get_form_model_by_code_mock:
            questionnaire = MagicMock(spec=FormModel)
            get_form_model_by_code_mock.return_value = questionnaire
            questionnaire.data_senders = ['rep1', 'rep2']
            questionnaire.is_void.return_value = False
            is_authorized = is_authorized_for_questionnaire(dbm, requested_user, 'form_code')

        self.assertFalse(is_authorized)

    def test_should_return_true_when_datasender_is_associated_with_questionnaire(self):
        dbm = MagicMock()
        requested_user = MagicMock()
        user_profile = MagicMock(spec=NGOUserProfile)
        user_profile.reporter_id = 'rep123'
        requested_user.get_profile.return_value = user_profile
        with patch('datawinners.xforms.views.get_form_model_by_code') as get_form_model_by_code_mock:
            questionnaire = MagicMock(spec=FormModel)
            get_form_model_by_code_mock.return_value = questionnaire
            questionnaire.data_senders = ['rep1', 'rep123']
            questionnaire.is_void.return_value = False
            is_authorized = is_authorized_for_questionnaire(dbm, requested_user, 'form_code')

        self.assertTrue(is_authorized)

    def test_should_return_true_when_requested_user_is_admin(self):
        dbm = MagicMock()
        requested_user = MagicMock()
        user_profile = MagicMock(spec=NGOUserProfile)
        user_profile.reporter = None
        requested_user.get_profile.return_value = user_profile
        is_authorized = is_authorized_for_questionnaire(dbm, requested_user, 'form_code')
        self.assertTrue(is_authorized)

@restrict_request_country
def dummy_form_list(request):
    return HttpResponse()




