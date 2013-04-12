# coding=utf-8
import json
from unittest import TestCase
from django.utils.translation import activate
from datawinners.activitylog.html_views import EditedDataSubmissionView, EditedRegistrationFormView, EditedProjectView

class TestHtmlViews(TestCase):
    '''Please put DJANGO_SETTINGS_MODULE=datawinners.settings in your environment variables for the test configuration you use
    in your IDE to run this test.'''

    def test_translate_edit_submissions_to_english(self):
        detail = {
            'received_on': 'Apr. 05, 2013, 08:01 AM',
            'status_changed': True,
            'changed_answers': {'question one': {'old': 23, 'new': 43},
                                'question two': {'old': 'text2', 'new': 'correct text'}}}

        expected = 'Submission Received on: Apr. 05, 2013, 08:01 AM<br/>Changed Status: "Error" to "Success"<br/>'\
                   'Changed Answers:<br/>'\
                   '<ul class="bulleted"><li>question one: "23" to "43"</li>'\
                   '<li>question two: "text2" to "correct text"</li></ul>'

        self.assertEqual(expected, EditedDataSubmissionView(detail).html())

    def test_translate_edit_submissions_to_french(self):
        activate('fr')
        self.maxDiff = None
        detail = {
            'received_on': 'Apr. 05, 2013, 08:01 AM',
            'status_changed': True,
            'changed_answers': {'question one': {'old': 23, 'new': 43},
                                'question two': {'old': 'text2', 'new': 'correct text'}}}

        expected = u'Soumission reçue le: Apr. 05, 2013, 08:01 AM<br/>Statut modifié: “Erreur” à “Succès”<br/>'\
                   u'Réponses modifiées:<br/>'\
                   u'<ul class="bulleted"><li>question one: "23" à "43"</li>'\
                   u'<li>question two: "text2" à "correct text"</li></ul>'
        actual = EditedDataSubmissionView(detail).html()
        activate('en')
        self.assertEqual(expected, actual)

    def test_should_return_the_translated_detail_for_edit_registration_form(self):
        detail = u'{"deleted": ["What is the clinic\'s mobile telephone number?"], '\
                 u'"added": ["new question"], "entity_type": "Clinic"}'

        detail_dict = json.loads(detail)
        expected = u'Subject Type: Clinic<br/>Added Questions: '\
                   u'<ul class="bulleted">'\
                   u'<li>new question</li>'\
                   u'</ul><br/>Deleted Questions: '\
                   u'<ul class="bulleted">'\
                   u'<li>What is the clinic\'s mobile telephone number?</li>'\
                   u'</ul>'

        self.assertEqual(expected, EditedRegistrationFormView(detail_dict).html())

    def test_should_return_the_translated_detail_for_project_edition(self):
        changed_details = u'{"deleted": ["added", "new add"]}'
        expected = u'Deleted Questions: <ul class="bulleted"><li>added</li><li>new add</li></ul>'
        self.assertEqual(EditedProjectView(json.loads(changed_details)).html(), expected)

        detail = u'{"changed_type": [{"type": "date", "label": "Question 8"}]}'
        self.assertEqual(EditedProjectView(json.loads(detail)).html(),
            u'Answer type changed to date for "Question 8"')

        self.maxDiff = None
        detail1 = u'{"deleted": ["What is associat\u00e9d entity?", "What is your nam\u00e9?", "What is age \u00f6f father?", "What is r\u00e9porting date?", "What is your blood group?", "What ar\u00e9 symptoms?", "What is the GPS code for clinic?", "Question 8"], "added": ["Which waterpoint are you reporting on?", "What is the reporting period for the activity?", "word", "number", "choices", "gps"], "Name": "minoa", "Language": "mg", "Entity_type": "waterpoint"}'
        expected = u'Name: minoa<br/>Language: mg<br/>Entity_type: waterpoint<br/>Added Questions: <ul class="bulleted"><li>Which waterpoint are you reporting on?</li><li>What is the reporting period for the activity?</li><li>word</li><li>number</li><li>choices</li><li>gps</li></ul><br/>Deleted Questions: <ul class="bulleted"><li>What is associat\xe9d entity?</li><li>What is your nam\xe9?</li><li>What is age \xf6f father?</li><li>What is r\xe9porting date?</li><li>What is your blood group?</li><li>What ar\xe9 symptoms?</li><li>What is the GPS code for clinic?</li><li>Question 8</li></ul>'
        self.assertEqual(EditedProjectView(json.loads(detail1)).html(), expected)
