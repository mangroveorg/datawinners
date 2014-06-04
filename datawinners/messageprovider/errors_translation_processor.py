from collections import OrderedDict
import mangrove.errors.MangroveException as ex
from django.utils.translation import get_language, gettext as _, activate

def data_object_not_found_formatter(exception, message):
    return message % (exception.data[0].capitalize(), _(exception.data[1]), str(exception.data[2]))


def default_formatter(exception, message):
    return message

def incorrect_date_formatter(exception, message):
    return message % (str(exception.data[1]), exception.data[0], exception.data[2])

def invalid_answer_formatter(exception, message):
    return message % (str(exception.data[1]), exception.data[0])

def datasender_not_linked_formatter(exception, message):
    return message.decode('utf-8') % (exception.data[0].capitalize(), exception.data[1])


messages_and_formatters = {
  ex.DataObjectNotFound: (u"%s with %s = %s not found.", data_object_not_found_formatter),
  ex.GeoCodeFormatException: (u"Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315", default_formatter),
  ex.IncorrectDate: (u"Answer %s for question %s is invalid. Expected date in %s format", incorrect_date_formatter),
  ex.AnswerWrongType: (u"Answer %s for question %s is of the wrong type.", invalid_answer_formatter),
  ex.AnswerTooLongException: (u"Answer %s for question %s is longer than allowed.", invalid_answer_formatter),
  ex.AnswerTooSmallException: (u"Answer %s for question %s is smaller than allowed.", invalid_answer_formatter),
  ex.AnswerTooBigException: (u"Answer %s for question %s is greater than allowed.", invalid_answer_formatter),
  ex.AnswerTooShortException: (u"Answer %s for question %s is shorter than allowed.", invalid_answer_formatter),
  ex.LatitudeNotFloat: (u'Answer must be in the following format: xx.xxxx yy.yyyy Example: -18.1324 27.6547', default_formatter),
  ex.LongitudeNotFloat: (u'Answer must be in the following format: xx.xxxx yy.yyyy Example: -18.1324 27.6547', default_formatter),
  ex.LatitudeNotInRange: (u'Invalid GPS value.', default_formatter),
  ex.AnswerHasTooManyValuesException: (u"Answer %s for question %s contains more than one value.", invalid_answer_formatter),
  ex.DatasenderIsNotLinkedException: (u"The Data Sender %s (%s) is not linked to your Questionnaire.", datasender_not_linked_formatter)
}

class TranslationProcessor(object):
    def __init__(self, form_model, response):
        self.form_model = form_model
        self.language_separator = '| |'
        if response is not None:
            self.validation_exception = [response.exception] + form_model.validation_exception
        else:
            self.validation_exception = form_model.validation_exception

    def process(self):
        error_msg_dict = OrderedDict()
        current_language = get_language()
        existing_language = ["en", "fr"]
        for language in existing_language:
            activate(language)
            for index, e in enumerate(self.validation_exception):
                message, formatter = messages_and_formatters.get(type(e), (None, None))
                if message is None: continue
                translated_message = _(message)
                formatted_message = formatter(e, translated_message)
                if index == len(self.validation_exception) -1 and \
                    existing_language.index(language) != len(existing_language)-1:
                    formatted_message += self.language_separator
                if not isinstance(formatted_message, unicode):
                    formatted_message = formatted_message.decode('utf-8')
                error_msg_dict.update({'%s%s' % (language, index +1): formatted_message})
        activate(current_language)
        return error_msg_dict