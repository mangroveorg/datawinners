from django.forms import ModelForm
from datawinners.accountmanagement.models import Organization

class OrganizationForm(ModelForm):
    class Meta:
        model = Organization

    def update(self):
        if self.is_valid():
            organization = Organization.objects.get(org_id = self.cleaned_data['org_id'])
            organization.name = self.cleaned_data['name']
            organization.sector = self.cleaned_data['sector']
            organization.addressline1 = self.cleaned_data['addressline1']
            organization.addressline2 = self.cleaned_data['addressline2']
            organization.city = self.cleaned_data['city']
            organization.state = self.cleaned_data['state']
            organization.country = self.cleaned_data['country']
            organization.zipcode = self.cleaned_data['zipcode']
            organization.office_phone = self.cleaned_data['office_phone']
            organization.website = self.cleaned_data['website']
            organization.org_id = self.cleaned_data['org_id']

            organization.save()
            return True
            
        
