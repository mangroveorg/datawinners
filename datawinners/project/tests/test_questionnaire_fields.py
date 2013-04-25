from unittest import TestCase
from project.questionnaire_fields import TextInputForFloat

class TestTextInputForFloat(TestCase):
    def test_has_not_changed_for_different_string_representation_of_same_float_value(self):
        text_input = TextInputForFloat()
        self.assertFalse(text_input._has_changed('22.0', '22'))

    def test_has_not_changed_for_same_float_values(self):
        text_input = TextInputForFloat()
        self.assertFalse(text_input._has_changed(22.00, 22))

    def test_has_not_changed_for_none_values(self):
        text_input = TextInputForFloat()
        self.assertFalse(text_input._has_changed(None, None))

    def test_has_changed_for_different_strings(self):
        text_input = TextInputForFloat()
        self.assertTrue(text_input._has_changed('testone', 'testtwo'))

    def test_has_changed_for_a_string_and_float(self):
        text_input = TextInputForFloat()
        self.assertTrue(text_input._has_changed('testone', 22))
