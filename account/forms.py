from django.forms import ModelForm
from datawinners.accountmanagement.models import Organization

class OrganizationForm(ModelForm):
    class Meta:
        model = Organization

    def update(self, posted_form, org_id):
        organization = Organization.objects.get(org_id = org_id)
        
