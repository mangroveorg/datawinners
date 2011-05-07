from django.forms.fields import CharField, RegexField
from django.forms.forms import Form


class ReporterRegistrationForm(Form):
    error_css_class = 'error'
    required_css_class = 'required'

    first_name = RegexField(regex="[^0-9.,\s@#$%&*~]*", max_length=30, error_message="Please enter a valid value containing only letters a-z or A-Z or symbols '`- ", required=True, label="* First Name")
    last_name = RegexField(regex="[^0-9.,\s@#$%&*~]*", max_length=30, error_message="Please enter a valid value containing only letters a-z or A-Z or symbols '`- ", required=True, label="* Last Name")
    telephone_number = CharField(required=True, label="* Telephone Number")
    commune = CharField(max_length=30, required=True, label="* Commune")
