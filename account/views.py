from django.contrib.auth.models import User, Group
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from datawinners.accountmanagement.models import Organization, NGOUserProfile
from datawinners.accountmanagement.forms import OrganizationForm, UserProfileForm

def is_admin(f):

    def wrapper(*args, **kw):
        user = args[0].user
        if not user.groups.filter(name = "NGO Admins").count() > 0:
            return HttpResponseNotFound()
        
        return f(*args, **kw)
    return wrapper

@login_required
@is_admin
def settings(request):
    profile_form = UserProfileForm()
    users = NGOUserProfile.objects.all()
    if request.method == 'GET':
        profile = request.user.get_profile()
        organization = Organization.objects.get(org_id=profile.org_id)
        organization_form = OrganizationForm(instance = organization)
        return render_to_response("account/settings.html", {'organization_form' : organization_form, 'profile_form' : profile_form, 'users' : users, 'current_page':'1'}, context_instance=RequestContext(request))
    
    if request.method == 'POST':
        organization = Organization.objects.get(org_id=request.POST["org_id"])
        organization_form = OrganizationForm(request.POST, instance = organization).update()
        return HttpResponseRedirect('/account/#tabs-1') if not organization_form.errors  else render_to_response("account/settings.html", {'organization_form' : organization_form, 'profile_form' : profile_form, 'users' : users, 'current_page':'1'}, context_instance=RequestContext(request))


@login_required
@is_admin
def new_user(request):
    if request.method == 'POST':
        org_id = request.user.get_profile().org_id
        form = UserProfileForm(request.POST)

        if form.is_valid():
            if User.objects.filter(username = form.cleaned_data['username']).count() > 0:
                form.errors['username'] = "Username already exists"
            if not form.errors:
                user = User.objects.create_user(form.cleaned_data['username'],form.cleaned_data['username'],'test123')
                user.first_name  = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                group = Group.objects.filter(name = "Project Managers")
                user.groups.add(group[0])
                user.save()
                ngo_user_profile = NGOUserProfile(user = user, title = form.cleaned_data['title'], office_phone = form.cleaned_data['office_phone'],
                                                  mobile_phone = form.cleaned_data['mobile_phone'], skype = form.cleaned_data['skype'], org_id = org_id)
                ngo_user_profile.save()
                return HttpResponseRedirect('/account/#tabs-2')
        
        
        profile = request.user.get_profile()
        organization = Organization.objects.get(org_id=profile.org_id)
        organization_form = OrganizationForm(instance = organization)
        users = NGOUserProfile.objects.all()
        return render_to_response("account/settings.html", {'organization_form' : organization_form, 'profile_form' : form,  'users' : users, 'current_page': '2'}, context_instance=RequestContext(request))


@login_required
@is_admin
def users(request):
    if request.method == 'GET':
        users = NGOUserProfile.objects.all()
        return render_to_response("account/list_users.html", {'users' : users}, context_instance=RequestContext(request))


@login_required
@is_admin
def edit_user(request):
    if request.method == 'GET':
        profile = request.user.get_profile()
        form = UserProfileForm(data = dict(title = profile.title, first_name = profile.user.first_name,
                                           last_name = profile.user.last_name,
                                           username = profile.user.username, office_phone = profile.office_phone,
                                           mobile_phone = profile.mobile_phone,skype = profile.skype))
        return render_to_response("account/edit_profile.html", {'form' : form}, context_instance=RequestContext(request))
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username = request.user.username)
            user.first_name  = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            ngo_user_profile = NGOUserProfile.objects.get(user = user)
            ngo_user_profile.title = form.cleaned_data['title']
            ngo_user_profile.office_phone = form.cleaned_data['office_phone']
            ngo_user_profile.mobile_phone = form.cleaned_data['mobile_phone']
            ngo_user_profile.skype = form.cleaned_data['skype']
            ngo_user_profile.save()
            return render_to_response("account/edit_profile.html", {'form' : form}, context_instance=RequestContext(request))

