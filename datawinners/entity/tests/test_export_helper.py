from datawinners.entity.entity_export_helper import get_subject_headers, get_submission_headers
from mangrove.bootstrap import initializer
from mangrove.utils.test_utils.mangrove_test_case import MangroveTestCase


class TestExcelHeaders(MangroveTestCase):
    def setUp(self):
        MangroveTestCase.setUp(self)
        initializer.run(self.manager)


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
            ["\n Enter a word", "\n Enter a number between 12-15.",
             "\n Enter the date in the following format: day.month.year",
             "\n Assign a unique ID for each Subject.", '\n Enter name of the location.',
             "\n Choose 1 or more answers from the list."], header_instructions)

        header_examples = self._get_header_component(headers, 2)
        self.assertEqual(
            ["\n\n ", "\n\n ", "\n\n Example: 25.12.2011",
             "\n\n Leave this column blank if you want DataWinners to assign an ID for you.", '\n\n Example: Nairobi',
             "\n\n Example: a or ab"], header_examples)

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

        headers = get_submission_headers(fields)

        headers_text = self._get_header_component(headers, 0)
        self.assertEqual(
            ["What is your name", "What is your age", "What is the reporting date",
             "What is the subject id",
             "Your choices"], headers_text)

        header_instructions = self._get_header_component(headers, 1)
        self.assertEqual(
            ["\n Enter a word", "\n Enter a number between 12-15.",
             "\n Enter the date in the following format: day.month.year",
             "\n Enter unique ID",
             "\n Choose 1 or more answers from the list."], header_instructions)

        header_examples = self._get_header_component(headers, 2)
        self.assertEqual(
            ["\n\n ", "\n\n ", "\n\n Example: 25.12.2011",
             "\n\n ",
             "\n\n Example: a or ab"], header_examples)
