import unittest

import requests
from requests.auth import HTTPDigestAuth

from testdata.test_data import url


class DataExtractionAPITestCase(unittest.TestCase):
    def setUp(self):
        self.DIGEST_CREDENTIALS = HTTPDigestAuth('tester150411@gmail.com', 'tester150411')
        self.WRONG_DIGEST_CREDENTIALS = HTTPDigestAuth('wrong_user_name', 'wrong_pass_word')

    def test_should_get_subject_data_by_subject_type_and_id(self):
        response = requests.get(url('/api/get_for_subject/clinic/cid001/'), auth=self.DIGEST_CREDENTIALS)
        self.assertEquals(response.status_code, 200)

    def test_should_return_authentication_required_status_when_query_subject_data_with_wrong_auth(self):
        response = requests.get(url('/api/get_for_subject/clinic/cid001/'), auth=self.WRONG_DIGEST_CREDENTIALS)
        self.assertEquals(response.status_code, 401)

    def test_should_return_authentication_required_status_when_query_subject_data_without_auth(self):
        response = requests.get(url('/api/get_for_subject/clinic/cid001/'))
        self.assertEquals(response.status_code, 401)

    def test_should_return_authentication_required_status_when_query_form_data_with_wrong_auth(self):
        response = requests.get(url('/api/get_for_form/cli/'), auth=self.WRONG_DIGEST_CREDENTIALS)
        self.assertEquals(response.status_code, 401)

    def test_should_return_authentication_required_status_when_query_form_data_without_auth(self):
        response = requests.get(url('/api/get_for_subject/clinic/cid001/'))
        self.assertEquals(response.status_code, 401)


    def test_should_return_authentication_required_status_when_query_register_data_with_wrong_auth(self):
        response = requests.get(url('/api/registereddata/clinic/'), auth=self.WRONG_DIGEST_CREDENTIALS)
        self.assertEquals(response.status_code, 401)

    def test_should_return_authentication_required_status_when_query_register_data_without_auth(self):
        response = requests.get(url('/api/get_for_subject/clinic/cid001/'))
        self.assertEquals(response.status_code, 401)

    def test_should_return_404_response_status_when_date_format_is_invalid(self):
        response = requests.get(url('/api/registereddata/clinic/2/'), auth=self.DIGEST_CREDENTIALS)
        self.assertEquals(response.status_code, 404)

    def test_should_get_form_data_by_form_code_and_only_start_date(self):
        response = requests.get(url('/api/get_for_form/cli/03-08-2012/'), auth=self.DIGEST_CREDENTIALS)
        self.assertEquals(response.status_code, 200)


        response = requests.get(url('/api/registereddata/clinic/01-08-2012/03082012/'), auth=self.DIGEST_CREDENTIALS)
        self.assertEquals(response.status_code, 404)



