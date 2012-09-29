from unittest import TestCase
from project.web_questionnaire_form_creator import SubjectQuestionFieldCreator

subject_data = [
    {'short_code': u'123abc',
     'id': '36998351094511e28aa3406c8f3de0f2',
     'cols': [u'lastlast', u'ff,Madagascar', '18.1324, 27.6547', u'123ABC']
    },
]

fields = ['name', 'location', 'geo_code', 'short_code']

class TestSubjectQuestionFieldCreator(TestCase):
    def test_build_subject_choice_data(self):
        creator = SubjectQuestionFieldCreator(None, None)

        data = creator._build_subject_choice_data(subject_data, fields)[0]
        self.assertEqual(u'123abc', data['unique_id'])
        self.assertEqual(u'lastlast', data['name'])

    def test_should_build_choice_from_subject(self):
        creator = SubjectQuestionFieldCreator(None, None)

        data = {'name': 'lastlast', 'location': u'ff,Madagascar', 'geo_code': '18.1324, 27.6547', 'short_code': u'123ABC','unique_id': '123abc'}

        choice = creator._data_to_choice(data)

        self.assertEqual((u'123abc', u'lastlast  (123ABC)'), choice)