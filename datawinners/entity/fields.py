from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator, MinLengthValidator
from django.utils.encoding import smart_unicode
import re
from django.forms.fields import RegexField
from django.utils.translation import ugettext as _
from django.forms.fields import DateField

EMPTY_VALUES = (None, '', [], (), {})

PHONE_NUMBER_REGEX = "^(\(?[0-9]*?\)?)?[0-9- ]+$"
PHONE_NUMBER_MAX_LENGTH = 15
PHONE_NUMBER_MIN_LENGTH = 5

class PhoneNumberField(RegexField):
    def __init__(self, max_length=None, min_length=None, error_message=None, *args, **kwargs):
        super(PhoneNumberField, self).__init__(PHONE_NUMBER_REGEX,
                                               max_length or PHONE_NUMBER_MAX_LENGTH,
                                               min_length or PHONE_NUMBER_MIN_LENGTH,
                                               error_message or _("Please enter a valid phone number."),
                                               *args,
                                               **kwargs)

    def validate_phone_number_for_filled_field(self, value):
        if value:
            length = len(value)
            message = _(u'Ensure this value has at least %(limit_value)d digits (it has %(show_value)d).')
            params = {'limit_value': PHONE_NUMBER_MIN_LENGTH, 'show_value': length}
            if length < 5:
                raise ValidationError(message % params)

    def validate(self, value):
        super(PhoneNumberField, self).validate(value)
        self.validate_phone_number_for_filled_field(value)

    def simplify_value(self, value):
        if value in EMPTY_VALUES:
            value = u''
        value = re.sub('[- \(\)+]', '', smart_unicode(value))
        return value

    def clean(self, value):
        value = self.simplify_value(value)
        super(PhoneNumberField, self).clean(value)
        return value

class DjangoDateField(DateField):
    def clean(self, value):
        if value:
            value = value.strip()
        super(DjangoDateField, self).clean(value)
        return value if value else None