from datawinners.entity.forms import ReporterRegistrationForm
from django.test.testcases import TestCase

class TestReporterRegistrationForm(TestCase):
    def test_should_remove_disabled_attribute_if_short_code_is_given(self):
        form = ReporterRegistrationForm()
        self.assertFalse(form.is_valid())
        self.assertTrue("disabled" in form.fields.get("short_code").widget.attrs)
        form = ReporterRegistrationForm(data={'short_code':"rep004"})
        self.assertFalse(form.is_valid())
        self.assertFalse("disabled" in form.fields.get("short_code").widget.attrs)
