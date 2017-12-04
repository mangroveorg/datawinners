# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from mangrove.errors.MangroveException import MangroveException
from django.utils.translation import ugettext as _

class ImportValidationError(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)

class InvalidEmailException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class NameNotFoundException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class QuestionCodeAlreadyExistsException(MangroveException):
    def __init__(self, message, param):
        self.message = _(message) % param