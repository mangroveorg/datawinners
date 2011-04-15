from django.contrib.localflavor.us.forms import USPhoneNumberField
from django.forms.fields import CharField, RegexField
from django.forms.forms import Form

class ReporterRegistrationForm(Form):
    error_css_class = 'error'
    required_css_class = 'required'

    first_name = RegexField(regex="^[a-zA-Z]*$", max_length=30, error_message="Please enter a valid value containing only letters a-z or A-Z.", required=True)
    last_name = RegexField(regex="^[a-zA-Z]*$", max_length=30, error_message="Please enter a valid value containing only letters a-z or A-Z.", required=True)
    telephone_number = USPhoneNumberField(required=True)
    commune = CharField(max_length=30, required=True)
    clinical_affiliation = CharField(max_length=30, required=False)


