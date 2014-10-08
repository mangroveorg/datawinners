import unittest

from mock import patch

from datawinners.common.admin.utils import get_admin_panel_filter, get_text_search_filter
from datawinners.common.constant import ADMIN_QUERY, ADMIN_PAGINATION, ADMIN_ORDER_COLUMN, ADMIN_ORDER_TYPE

class TestUtils(unittest.TestCase):

    def test_should_filter_out_query_and_ordering_admin_keys_and_return_filtered_dictionary(self):
        someKey = 'DeliveredAt'
        some_value = 'someDate'
        getRequestParameters = {ADMIN_QUERY: 'junk', ADMIN_PAGINATION: 'junk', ADMIN_ORDER_COLUMN: 'junk', ADMIN_ORDER_TYPE: 'junk', someKey: some_value}

        admin_panel_filter = get_admin_panel_filter(getRequestParameters)

        self.assertEquals(len(admin_panel_filter), 1)
        self.assertEquals(admin_panel_filter[someKey], some_value)

    def test_should_get_empty_Q_object_if_no_search_fields(self):
        with patch('datawinners.common.admin.utils.Q') as MockClass:
            instance = MockClass.return_value

            getRequestParameters = {ADMIN_QUERY: "bla"}
            textSearchFilter = get_text_search_filter(getRequestParameters, None)
            self.assertEquals(textSearchFilter, instance)

    def test_should_get_empty_Q_object_if_no_admin_query_parameters_in_request_parameters(self):
        with patch('datawinners.common.admin.utils.Q') as MockClass:
            instance = MockClass.return_value

            textSearchFilter = get_text_search_filter({}, ['field1', 'field2'])
            self.assertEquals(textSearchFilter, instance)

