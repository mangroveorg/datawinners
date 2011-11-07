from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator, MinLengthValidator
from django.forms.forms import BoundField
from django.forms.widgets import Select
from django.utils.encoding import smart_unicode, force_unicode
from django.utils.html import conditional_escape, escape
import re
from django.forms.fields import RegexField, CharField
from django.utils.translation import ugettext as _
from datawinners.accountmanagement.phone_country_code import PHONE_COUNTRY_CODE

EMPTY_VALUES = (None, '', [], (), {})

PHONE_NUMBER_REGEX = "^(\(?[0-9]*?\)?)?[0-9- ]+$"
PHONE_NUMBER_MAX_LENGTH = 15
PHONE_NUMBER_MIN_LENGTH = 5
class PhoneCountryCodeSelectField(CharField):
    def __init__(self, max_length=None, min_length=None,data_for=None, *args, **kwargs):
        super(PhoneCountryCodeSelectField, self).__init__(max_length, min_length, *args, **kwargs)
        self.widget = PhoneCountryCodeSelect(attrs={'class': 'width-200px'})
        self.data_for = data_for
        
    def clean(self, value):
        super(PhoneCountryCodeSelectField, self).clean(value)
        self.data_for.country_code = value
        return value


class PhoneCountryCodeSelect(Select):
    def __init__(self, attrs=None, choices=PHONE_COUNTRY_CODE):
        super(PhoneCountryCodeSelect, self).__init__(attrs, choices)

    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_unicode(option_value)
        selected_html = (option_value in selected_choices) and u' selected="selected"' or ''
        title = conditional_escape(force_unicode(option_label))
        return u'<option value="%s" title="%s" %s>%s</option>' % (
            escape(option_value),title, selected_html,
            title+" "+escape(option_value))
    
class PhoneNumberField(RegexField):
    def __init__(self, max_length=None, min_length=None, error_message=None, *args, **kwargs):
        super(PhoneNumberField, self).__init__(PHONE_NUMBER_REGEX,
                                               max_length or PHONE_NUMBER_MAX_LENGTH,
                                               min_length or PHONE_NUMBER_MIN_LENGTH,
                                               error_message or _("Please enter a valid phone number."),
                                               *args,
                                               **kwargs)
        self.country_code = ''

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
        return self.country_code + value
