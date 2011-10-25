# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from mangrove.errors.MangroveException import TrialAccountExpiredException
from datawinners.accountmanagement.forms import OrganizationForm, UserProfileForm, EditUserProfileForm
from datawinners.accountmanagement.models import Organization, NGOUserProfile
from django.contrib.auth.views import login
from datawinners.main.utils import get_database_manager
from datawinners.project.models import get_all_projects
from django.utils.translation import ugettext as _
from datawinners.project.models import Project

def registration_complete(request, user=None):
    return render_to_response('registration/registration_complete.html')


def custom_login(request, template_name, authentication_form):
    if request.user.is_authenticated():
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    else:
        try:
            return login(request, template_name=template_name, authentication_form=authentication_form)
        except TrialAccountExpiredException:
            return HttpResponseRedirect(settings.TRIAL_EXPIRED_URL)

def is_admin(f):
    def wrapper(*args, **kw):
        user = args[0].user
        if not user.groups.filter(name="NGO Admins").count() > 0:
            return HttpResponseRedirect(settings.HOME_PAGE)

        return f(*args, **kw)

    return wrapper

def project_has_web_device(f):
    def wrapper(*args, **kw):
        request = args[0]
        user = request.user
        dbm = get_database_manager(user)
        project_id = kw["project_id"]
        project = Project.load(dbm.database, project_id)
        if "web" not in project.devices:
            referer = settings.HOME_PAGE
            return HttpResponseRedirect(referer)
        return f(*args, **kw)
    return wrapper

def is_datasender(f):
    def wrapper(*args, **kw):
        user = args[0].user
        if user.groups.filter(name="Data Senders").count() > 0:
            return HttpResponseRedirect(settings.DATASENDER_DASHBOARD)

        return f(*args, **kw)

    return wrapper


def is_datasender_allowed(f):
    def wrapper(*args, **kw):
        user = args[0].user
        projects = get_all_projects(get_database_manager(user), user.get_profile().reporter_id)
        project_ids = [project.id for project in projects]
        project_id = kw['project_id']
        if not project_id in project_ids:
            return HttpResponseRedirect(settings.DATASENDER_DASHBOARD)

        return f(*args, **kw)
    return wrapper

def is_new_user(f):
    def wrapper(*args, **kw):
        user = args[0].user
        if not len(get_all_projects(get_database_manager(args[0].user))) and not user.groups.filter(
            name="Data Senders").count() > 0:
            return HttpResponseRedirect("/start?page=" + args[0].path)

        return f(*args, **kw)

    return wrapper

@login_required(login_url='/login')
@is_admin
def settings(request):
    if request.method == 'GET':
        profile = request.user.get_profile()
        organization = Organization.objects.get(org_id=profile.org_id)
        organization_form = OrganizationForm(instance=organization)
        return render_to_response("accountmanagement/account/org_settings.html",
                {'organization_form': organization_form}, context_instance=RequestContext(request))

    if request.method == 'POST':
        organization = Organization.objects.get(org_id=request.POST["org_id"])
        organization_form = OrganizationForm(request.POST, instance=organization).update()
        message = "" if organization_form.errors else _('Settings have been updated successfully')
        return render_to_response("accountmanagement/account/org_settings.html",
                {'organization_form': organization_form, 'message': message}, context_instance=RequestContext(request))


@login_required(login_url='/login')
@is_admin
def new_user(request):
    add_user_success = False
    if request.method == 'GET':
        profile_form = UserProfileForm()
        return render_to_response("accountmanagement/account/add_user.html", {'profile_form': profile_form},
                                  context_instance=RequestContext(request))

    if request.method == 'POST':
        org_id = request.user.get_profile().org_id
        form = UserProfileForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            if not form.errors:
                user = User.objects.create_user(username, username, 'test123')
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                group = Group.objects.filter(name="Project Managers")
                user.groups.add(group[0])
                user.save()
                ngo_user_profile = NGOUserProfile(user=user, title=form.cleaned_data['title'],
                                                  office_phone=form.cleaned_data['office_phone'],
                                                  mobile_phone=form.cleaned_data['mobile_phone'],
                                                  skype=form.cleaned_data['skype'], org_id=org_id)
                ngo_user_profile.save()
                reset_form = PasswordResetForm({"email": username})
                reset_form.is_valid()
                reset_form.save()
                form = UserProfileForm()
                add_user_success = True

        return render_to_response("accountmanagement/account/add_user.html", {'profile_form': form, 'add_user_success': add_user_success},
                                  context_instance=RequestContext(request))


@login_required(login_url='/login')
@is_admin
def users(request):
    if request.method == 'GET':
        org_id = request.user.get_profile().org_id
        users = NGOUserProfile.objects.filter(org_id=org_id)
        return render_to_response("accountmanagement/account/users_list.html", {'users': users},
                                  context_instance=RequestContext(request))


@login_required(login_url='/login')
def edit_user(request):
    if request.method == 'GET':
        profile = request.user.get_profile()
        form = EditUserProfileForm(data=dict(title=profile.title, first_name=profile.user.first_name,
                                             last_name=profile.user.last_name,
                                             username=profile.user.username, office_phone=profile.office_phone,
                                             mobile_phone=profile.mobile_phone, skype=profile.skype))
        return render_to_response("accountmanagement/profile/edit_profile.html", {'form': form},
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
        form = EditUserProfileForm(request.POST)
        message = ""
        if form.is_valid():
            user = User.objects.get(username=request.user.username)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            ngo_user_profile = NGOUserProfile.objects.get(user=user)
            ngo_user_profile.title = form.cleaned_data['title']
            ngo_user_profile.office_phone = form.cleaned_data['office_phone']
            ngo_user_profile.mobile_phone = form.cleaned_data['mobile_phone']
            ngo_user_profile.skype = form.cleaned_data['skype']
            ngo_user_profile.save()
            message = _('Profile has been updated successfully')
        return render_to_response("accountmanagement/profile/edit_profile.html", {'form': form, 'message': message},
                                  context_instance=RequestContext(request))

def trial_expired(request):
    return render_to_response("registration/trail_account_expired_message.html")
