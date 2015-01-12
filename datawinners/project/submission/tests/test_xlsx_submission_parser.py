from datawinners.project.submission.submission_import import XlsxSubmissionParser
from unittest import TestCase
import os

class TestXlsxSubmissionParser(TestCase):
    def test_should_parse_xlsx_content(self):
        file_name = "import-submission.xlsx"
        expected = [[u'I am submitting this data on behalf of'
            '\n\nIf you are sending data on behalf of someone, you can enter their Data Sender ID. '
            'Otherwise you can leave it blank.\n\nExample: rep42', u'mkjkl\n\nAnswer must be a word'],
            [u'', u'worida']]
        dirname = os.path.dirname(__file__)
        abspath = os.path.abspath(dirname)
        file_path = os.path.join(abspath, file_name)
        file_contents = open(file_path).read()
        
        data = XlsxSubmissionParser().parse(file_contents)
        self.assertEqual(expected, data)