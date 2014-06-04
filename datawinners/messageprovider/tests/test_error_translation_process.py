from django.test import TestCase
from datawinners.messageprovider.errors_translation_processor import TranslationProcessor
from mock import Mock, patch
from mangrove.form_model.form_model import FormModel
import mangrove.errors.MangroveException as ex
from collections import OrderedDict

class TestErrorTranslationProcess(TestCase):

    def setUp(self):
        self.form_model = Mock(spec=FormModel)
        self.form_model.validation_exception = [ex.AnswerWrongType('q1', 'number'), ex.AnswerTooLongException('q2', 'longword', 4),
                                      ex.AnswerTooBigException('q3', 300)]

    def test_should_process_translation(self):
        expected = OrderedDict([('en1', u'Answer number for question q1 is of the wrong type.'),
                                ('en2', u'Answer longword for question q2 is longer than allowed.'),
                                ('en3', u'Answer 300 for question q3 is greater than allowed.| |'),
                                ('fr1', u'Le type de la r\xe9ponse number pour la question "q1" est erron\xe9.'),
                                ('fr2', u'La r\xe9ponse longword \xe0 la question q2 est plus longue que la limite autoris\xe9e.'),
                                ('fr3', u'La r\xe9ponse 300 pour la question "q3" est sup\xe9rieure \xe0 ce qui est permise.')])
        translated = TranslationProcessor(self.form_model, None).process()
        self.assertEqual(expected, translated)
  