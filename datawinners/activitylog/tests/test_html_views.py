# coding=utf-8
from unittest import TestCase
from django.utils.translation import activate
from activitylog.html_views import EditedDataSubmissionView

class TestHtmlViews(TestCase):
    '''Please put DJANGO_SETTINGS_MODULE=datawinners.settings in your environment variables for the test configuration you use
    in your IDE to run this test.'''

    def test_translate_edit_submissions_to_english(self):
        detail = {
            'received_on': 'Apr. 05, 2013, 08:01 AM',
            'status_changed': True,
            'changed_answers': {'question one': {'old': 23, 'new': 43},
                                'question two': {'old': 'text2', 'new': 'correct text'}}}

        expected = ['Submission Received on: Apr. 05, 2013, 08:01 AM', 'Changed Status: "Error" to "Success"',\
                    'Changed Answers:',
                    '<ul class="bulleted"><li>question one: "23" to "43"</li>'\
                    '<li>question two: "text2" to "correct text"</li></ul>']

        self.assertEqual(expected, EditedDataSubmissionView(detail).html())

    def test_translate_edit_submissions_to_french(self):
        activate('fr')
        detail = {
            'received_on': 'Apr. 05, 2013, 08:01 AM',
            'status_changed': True,
            'changed_answers': {'question one': {'old': 23, 'new': 43},
                                'question two': {'old': 'text2', 'new': 'correct text'}}}

        expected = [u'Soumission reçue le: Apr. 05, 2013, 08:01 AM', u'Statut modifié: “Erreur” à “Succès”',\
                    u'Réponses modifiées',
                    u'<ul class="bulleted"><li>question one: "23" à "43"</li>'\
                    u'<li>question two: "text2" à "correct text"</li></ul>']
        actual = EditedDataSubmissionView(detail).html()
        activate('en')
        self.assertEqual(expected, actual)
