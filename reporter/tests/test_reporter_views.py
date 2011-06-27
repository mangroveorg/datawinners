# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import unittest
from datawinners.reporter.views import _get_telephone_number

class TestReporterViews(unittest.TestCase):

    def test_should_get_telephone_number_without_any_non_numeric_characters(self):
        tel_no = _get_telephone_number("123-456!789")
        self.assertEqual("123456789", tel_no)
    #TODO find a way to write the test
#    def test_should_display_register_reporter_form(self):
#        request = Mock(spec=HttpRequest)
#        request.method = "GET"
#        request.user = ""
#        with patch.object(django.shortcuts, 'render_to_response') as render_to_response:
#            result = register(request)

