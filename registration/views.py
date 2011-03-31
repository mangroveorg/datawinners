# Create your views here.
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.registration.forms import RegistrationForm
from django.contrib import messages

#TODO: create org id from the creator
# Set the user as super user
from datawinners.registration.models import Organization, NGOUser

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid() :
#            title = form.cleaned_data.get('title'),
#            org_id=OrganizationIdCreator().generateId()
            organization = Organization(name = form.cleaned_data.get('organization_name'), sector = form.cleaned_data.get('organization_sector')
                                             , addressline1 = form.cleaned_data.get('organization_addressline1'), addressline2 = form.cleaned_data.get('organization_addressline2')
                                             , city = form.cleaned_data.get('organization_city'), state = form.cleaned_data.get('organization_state')
                                             , country = form.cleaned_data.get('organization_country'), zipcode = form.cleaned_data.get('organization_zipcode')
                                             , office_phone = form.cleaned_data.get('organization_office_phone'), website = form.cleaned_data.get('organization_website'),org_id='AW1234'
                                             )
            user = NGOUser.objects.create_superuser(username=form.cleaned_data.get('email'),email=form.cleaned_data.get('email'), password = form.cleaned_data.get('password'))
            user.title = form.cleaned_data.get('title')
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            organization.save()
            user.save()

            messages.success(request,"You have successfully registered organization with id : %s."%(1234,))
            return render_to_response('registration/registration_success.html', {'organization' : organization,'user':user}, context_instance=RequestContext(request))

    else:
        form = RegistrationForm()
    return render_to_response('registration/register.html', {'form' : form}, context_instance=RequestContext(request))

@login_required
def home(request):
    return render_to_response('registration/home.html',context_instance=RequestContext(request))
