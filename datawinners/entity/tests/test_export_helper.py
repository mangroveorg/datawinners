import unittest
from mangrove.datastore.database import DatabaseManager
from mangrove.form_model.form_model import FormModel
from mock import Mock
from datawinners.entity.entity_export_helper import get_subject_headers, get_submission_headers


class TestExcelHeaders(unittest.TestCase):
    def _get_header_component(self, headers, parameter):
        header_text = []
        for header in headers:
            self.assertTrue(isinstance(header, tuple))
            self.assertEqual(len(header), 3)
            header_text.append(header[parameter][0])
        return header_text

    def test_should_get_header_information_for_subject_excel(self):
        fields = [{"name": "first name", "code": 'q1', "label": 'What is your name', "entity_question_flag": False,
                   "type": "text"},
                  {"name": "age", "code": 'q2', "label": 'What is your age', "type": "integer", "constraints": [
                      [
                          "range",
                          {
                              "max": "15",
                              "min": "12"
                          }
                      ]
                  ]},
                  {"name": "reporting date", "code": 'q3', "label": 'What is the reporting date',
                   "date_format": "dd.mm.yyyy", "type": "date"},
                  {"name": "eid", "code": 'eid', "label": 'What is the subject id', "entity_question_flag": True,
                   "type": "text"},
                  {"name": "location", "code": 'q4', "label": 'What is the location', "type": "list"},
                  {"name": "choices", "code": 'q5', "label": 'Your choices', "type": "select"}]

        headers = get_subject_headers(fields)

        headers_text = self._get_header_component(headers, 0)
        self.assertEqual(
            ["What is your name", "What is your age", "What is the reporting date",
             "What is the subject id", 'What is the location',
             "Your choices"], headers_text)

        header_instructions = self._get_header_component(headers, 1)
        self.assertEqual(
            ["\nAnswer must be a word", "\nEnter a number between 12-15.",
             "\nAnswer must be a date in the following format: day.month.year",
             "\nAssign a unique ID for each Subject.", '\nEnter name of the location.',
             "\nEnter 1 or more answers from the list."], header_instructions)

        header_examples = self._get_header_component(headers, 2)
        self.assertEqual(
            ["\n\n", "\n\n", "\n\nExample: 25.12.2011",
             "\n\nLeave this column blank if you want DataWinners to assign an ID for you.", '\n\nExample: Nairobi',
             "\n\nExample: a or ab"], header_examples)

    def test_should_get_header_information_for_submission_excel(self):
        fields = [{"name": "first name", "code": 'q1', "label": 'What is your name', "entity_question_flag": False,
                   "type": "text"},
                  {"name": "age", "code": 'q2', "label": 'What is your age', "type": "integer", "constraints": [
                      [
                          "range",
                          {
                              "max": "15",
                              "min": "12"
                          }
                      ]
                  ]},
                  {"name": "reporting date", "code": 'q3', "label": 'What is the reporting date',
                   "date_format": "dd.mm.yyyy", "type": "date"},
                  {"name": "eid", "code": 'eid', "label": 'What is the subject id', "entity_question_flag": True,
                   "type": "text"},
                  {"name": "choices", "code": 'q5', "label": 'Your choices', "type": "select"}]
        form_model = FormModel(Mock(spec=DatabaseManager), name="some_name", entity_type=['test'], form_code="cli00_mp", fields=[], type="type1")

        headers = get_submission_headers(fields, form_model)

        headers_text = self._get_header_component(headers, 0)
        self.assertEqual(
            ["What is your name", "What is your age", "What is the reporting date",
             "What is the subject id",
             "Your choices"], headers_text)

        header_instructions = self._get_header_component(headers, 1)
        self.assertEqual(
            ["\n\nAnswer must be a word", "\n\nEnter a number between 12-15.",
             "\n\nAnswer must be a date in the following format: day.month.year",
             "\n\nEnter the unique ID for each test.\nYou can find the test List on the My Subjects page.",
             "\n\nEnter 1 or more answers from the list."], header_instructions)

        header_examples = self._get_header_component(headers, 2)
        self.assertEqual(
            ["\n\n", "\n\n", "\n\nExample: 25.12.2011",
             "\n\nExample: cli01",
             "\n\nExample: a or ab"], header_examples)
