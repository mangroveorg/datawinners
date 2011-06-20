from django.forms import ModelForm
from accountmanagement.models import Organization

class OrganizationForm(ModelForm):
    class Meta:
        model = Organization
