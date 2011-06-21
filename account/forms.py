from django.forms import ModelForm
from datawinners.accountmanagement.models import Organization

class OrganizationForm(ModelForm):
    class Meta:
        model = Organization

    def update(self):
        if self.is_valid():
            self.save()
        
        return self
            
        
