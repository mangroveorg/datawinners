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




