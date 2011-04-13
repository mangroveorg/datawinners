from django.db.models.fields import TextField
from django.forms.fields import CharField
from django.forms.forms import Form

class ReporterRegistrationForm(Form):
    first_name = CharField(max_length=30, required=True)
    last_name = CharField(max_length=30, required=True)
    telephone_number = CharField(max_length=30, required=True)
    commune = CharField(max_length=30, required=True)
    clinical_affiliation = CharField(max_length=30, required=False)


