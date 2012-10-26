import unittest
from support.delete_redundant_language_settings import delete_label_language_setting_on_form_model, delete_label_language_setting_on_field, delete_text_language_setting_on_field_choices, delete_language_redundant_settings

form_model_row_with_multi_labels = """
{
   "name": "AIDS",
   "entity_type": [
       "clinic"
   ],
   "label": {
       "fr": "french",
       "en": "Aids form_model"
   },
   "metadata": {
       "activeLanguages": "en"
   }
}
"""

form_model_row_without_activeLanguages_label = """
{
   "name": "AIDS",
   "entity_type": [
       "clinic"
   ],
   "label": {
       "mg": "Aids form_model",
       "fr": "french"
   },
   "metadata": {
       "activeLanguages": "en"
   }
}
"""

form_model_row = """
{
   "name": "AIDS",
   "entity_type": [
       "clinic"
   ],
   "label": {
       "en": "Aids form_model"
   },
   "json_fields": [
       {
           "code": "NA",
           "name": "What is your name?",
           "language": "en",
           "label": {
               "en": "Name"
           }
       },
       {
           "code": "FA",
           "name": "What is age of father?",
           "label": {
               "en": "Father age",
               "fr": "What is age of father?"
           },
       },
       {
           "code": "BG",
           "name": "What is your blood group?",
           "language": "mg",
           "label": {
               "mg": "Blood Group",
               "fr": "What is your blood group?"
           },
           "choices": [
               {
                   "text": {
                       "en": "O+",
                       "fr": "fr O+"
                   },
                   "val": "a"
               },
               {
                   "text": {
                       "mg": "en O-",
                       "fr": "fr O-"
                   },
                   "val": "b"
               },
               {
                   "text": {
                       "en": "AB"
                   },
                   "val": "c"
               },
               {
                   "text": {
                       "fr": "fr B+",
                       "en": "B+"
                   },
                   "val": "d"
               }
           ]
       }
   ],
   "state": "Active",
   "document_type": "FormModel",
   "form_code": "cli015",
   "metadata": {
       "activeLanguages": ["en", "fr"]
   }
}
"""

expect_form_model_row = """
{
   "name": "AIDS",
   "entity_type": [
       "clinic"
   ],
   "label": "Aids form_model",
   "json_fields": [
       {
           "code": "NA",
           "name": "What is your name?",
           "label": "Name"
       },
       {
           "code": "FA",
           "name": "What is age of father?",
           "label": "Father age",
       },
       {
           "code": "BG",
           "name": "What is your blood group?",
           "label": "Blood Group",
           "choices": [
               {
                   "text": "O+",
                   "val": "a"
               },
               {
                   "text": "en O-",
                   "val": "b"
               },
               {
                   "text": "AB",
                   "val": "c"
               },
               {
                   "text": "B+",
                   "val": "d"
               }
           ]
       }
   ],
   "state": "Active",
   "document_type": "FormModel",
   "form_code": "cli015",
   "metadata": {
       "activeLanguages": ["en", "fr"]
   }
}
"""

class TestDeleteLanguageSettings(unittest.TestCase):
    def setUp(self):
        self.form_model_dict = eval(form_model_row)
        self.expected_form_model_dict = eval(expect_form_model_row)
        self.active_language = self.form_model_dict["metadata"]["activeLanguages"]
        if isinstance(self.active_language, list):
            self.active_language = self.active_language[0]

    def test_should_delete_label_language_setting_on_form_model_when_there_is_label_of_active_language(self):
        form_model_dict = delete_label_language_setting_on_form_model(self.form_model_dict, self.active_language)

        self.assertEqual(form_model_dict['label'], self.expected_form_model_dict['label'])

    def test_should_delete_label_language_setting_on_form_model_when_there_are_multiple_labels_including_one_with_active_language(self):
        form_model_row_with_multi_labels_dict = eval(form_model_row_with_multi_labels)
        form_model_dict = delete_label_language_setting_on_form_model(form_model_row_with_multi_labels_dict, self.active_language)

        self.assertEqual(form_model_dict['label'], self.expected_form_model_dict['label'])

    def test_should_delete_label_language_setting_on_form_model_when_there_are_labels_without_active_language(self):
        form_model_without_label_of_active_language = eval(form_model_row_without_activeLanguages_label)
        form_model_dict = delete_label_language_setting_on_form_model(form_model_without_label_of_active_language, self.active_language)

        self.assertEqual(form_model_dict['label'], self.expected_form_model_dict['label'])

    def test_should_delete_label_language_setting_on_field(self):
        form_model_dict = delete_label_language_setting_on_field(self.form_model_dict, self.active_language)

        questions = form_model_dict['json_fields']
        expected_questions = self.expected_form_model_dict['json_fields']
        for question, expected_question in zip(questions, expected_questions):
            self.assertEqual(question['label'], expected_question['label'])
            self.assertFalse(question.has_key('language'))

    def test_should_delete_text_language_setting_on_field_choices(self):
        form_model_dict = delete_text_language_setting_on_field_choices(self.form_model_dict, self.active_language)

        questions = form_model_dict['json_fields']
        expected_questions = self.expected_form_model_dict['json_fields']
        for question, expected_question in zip(questions, expected_questions):
            if question.has_key('choices'):
                self.assertEqual(question['choices'], expected_question['choices'])

    def test_should_delete_language_redundant_settings(self):
        form_model_dict = delete_language_redundant_settings(self.form_model_dict)

        self.assertEqual(self.expected_form_model_dict, form_model_dict)


