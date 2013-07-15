from django.utils import unittest
from mock import Mock
from datawinners.alldata.views import get_entity_list_by_type
from datawinners.tests.data import DEFAULT_TEST_ORG_ID

class TestDataExport(unittest.TestCase):

    def _get_request_mock(self,org_id):
        request = Mock()
        request.user = Mock()
        mock_profile = Mock()
        mock_profile.org_id = Mock(return_value=org_id)
        mock_profile.reporter = None
        request.user.get_profile = Mock(return_value=mock_profile)
        return request

    def test_should_return_empty_entity_list_when_entity_type_is_None(self):
        request = self._get_request_mock(DEFAULT_TEST_ORG_ID)
        self.assertEqual(len(get_entity_list_by_type(request, None).content), 0)
