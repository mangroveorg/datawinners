from django.contrib.localflavor.us.forms import USPhoneNumberField
from django.contrib.localflavor.us.models import PhoneNumberField
from django.db.models.fields import TextField
from django.forms.fields import CharField
from django.forms.forms import Form

class ReporterRegistrationForm(Form):
    error_css_class = 'error'
    required_css_class = 'required'

    first_name = CharField(max_length=30, required=True)
    last_name = CharField(max_length=30, required=True)
    telephone_number = USPhoneNumberField(required=True)
    commune = CharField(max_length=30, required=True)
    clinical_affiliation = CharField(max_length=30, required=False)


