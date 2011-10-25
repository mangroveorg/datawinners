from django.utils.encoding import smart_unicode
import re
from django.forms.fields import RegexField
from django.utils.translation import ugettext as _

EMPTY_VALUES = (None, '', [], (), {})

PHONE_NUMBER_REGEX = "^(\+[0-9 ]*?)?(\(?[0-9]*?\)?)?[0-9- ]+$"
PHONE_NUMBER_MAX_LENGTH = 20
PHONE_NUMBER_MIN_LENGTH = 5

class PhoneNumberField(RegexField):
    def __init__(self, max_length=None, min_length=None, error_message=None, *args, **kwargs):
        super(PhoneNumberField, self).__init__(PHONE_NUMBER_REGEX,
                                               max_length or PHONE_NUMBER_MAX_LENGTH,
                                               min_length or PHONE_NUMBER_MIN_LENGTH,
                                               error_message or _("Please enter a valid phone number."),
                                               *args,
                                               **kwargs)

    def clean(self, value):
        super(PhoneNumberField, self).clean(value)
        if value in EMPTY_VALUES:
            return u''
        value = re.sub('[- \(\)+]', '', smart_unicode(value))
        return value



