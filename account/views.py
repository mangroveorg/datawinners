from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.accountmanagement.models import Organization, NGOUserProfile
from datawinners.accountmanagement.forms import OrganizationForm, UserProfileForm

@login_required(login_url='/login')
def settings(request):
    if request.method == 'GET':
        profile = request.user.get_profile()
        organization = Organization.objects.get(org_id=profile.org_id)
        organization_form = OrganizationForm(instance = organization)
        return render_to_response("account/settings.html", {'organization_form' : organization_form}, context_instance=RequestContext(request))

    if request.method == 'POST':
        organization = Organization.objects.get(org_id=request.POST["org_id"])
        organization_form = OrganizationForm(request.POST, instance = organization).update()

        return HttpResponseRedirect('/account') if not organization_form.errors  else render_to_response("account/settings.html", {'organization_form' : organization_form}, context_instance=RequestContext(request))


@login_required
def new_user(request):
    if request.method == 'GET':
        profile_form = UserProfileForm()
        return render_to_response("account/new_user.html", {'profile_form' : profile_form}, context_instance=RequestContext(request))
    if request.method == 'POST':
        org_id = request.user.get_profile().org_id
        form = UserProfileForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(form.cleaned_data['username'],form.cleaned_data['username'],'test123')
            user.first_name  = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            ngo_user_profile = NGOUserProfile(user = user, title = form.cleaned_data['title'], office_phone = form.cleaned_data['office_phone'],
                           mobile_phone = form.cleaned_data['mobile_phone'], skype = form.cleaned_data['skype'], org_id = org_id)
            ngo_user_profile.save()
            return HttpResponseRedirect('/account')

        print form.errors
        return render_to_response("account/new_user.html", {'profile_form' : form}, context_instance=RequestContext(request))
