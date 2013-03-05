from datetime import datetime
import unittest
from project.submission_utils.submission_formatter import SubmissionFormatter, NULL

today = datetime.utcnow().strftime("%d.%m.%Y")

class SubmissionFormatterTest(unittest.TestCase):
    def test_should_format_field_values_to_list_presentation(self):
        raw_values = [
            [('Clinic-One', 'cli14'), '01.01.2012', today, ('name', 'id', 'from'), ['one', 'two', 'three'], ['B+']]]
        formatted_field_value = SubmissionFormatter().get_formatted_values_for_list(raw_values,
            '%s<span class="small_grey">%s</span>')
        expected = [['Clinic-One<span class="small_grey">cli14</span>', '01.01.2012', today,
                     'name<span class="small_grey">id</span>', 'one, two, three', 'B+']]

        self.assertEqual(expected, formatted_field_value)

    def test_should_format_field_values_to_list_exported(self):
        raw_values = [
            [('Clinic-One', 'cli14'), '01.01.2012', today, ('name', 'id', 'from'), ['one', 'two', 'three'], ['B+']]]
        formatted_field_value = SubmissionFormatter().get_formatted_values_for_list(raw_values, '%s(%s)')
        expected = [['Clinic-One(cli14)', '01.01.2012', today, 'name(id)', 'one, two, three', 'B+']]
        self.assertEqual(expected, formatted_field_value)

    def test_should_show_NULL_string_as_values_for_newly_created_questions(self):
        raw_values = [
            [('Clinic-One', 'cli14'), '01.01.2012', today, ('name', 'id', 'from'), ['one', 'two', 'three'], ['B+'],
             None, ""]]
        formatted_field_value = SubmissionFormatter().get_formatted_values_for_list(raw_values)
        expected = [['Clinic-One<span class="small_grey">cli14</span>', '01.01.2012', today,
                     'name<span class="small_grey">id</span>', 'one, two, three', 'B+', NULL, NULL]]
        self.assertEqual(expected, formatted_field_value)

    def test_should_not_change_zero_number_value_to_null_string(self):
        raw_values = [
            [('Clinic-One', 'cli14'), '01.01.2012', today, ('name', 'id', 'from'), ['one', 'two', 'three'], ['B+'],
             None, "", 0.0]]
        formatted_field_value = SubmissionFormatter().get_formatted_values_for_list(raw_values)
        expected = [['Clinic-One<span class="small_grey">cli14</span>', '01.01.2012', today,
                     'name<span class="small_grey">id</span>', 'one, two, three', 'B+', NULL, NULL, 0]]
        self.assertEqual(expected, formatted_field_value)
