# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User, Group
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.loader import render_to_string
from datawinners.accountmanagement.post_activation_events import make_user_as_a_datasender
from datawinners.settings import HNI_SUPPORT_EMAIL_ID, EMAIL_HOST_USER

from mangrove.errors.MangroveException import AccountExpiredException
from datawinners.accountmanagement.forms import OrganizationForm, UserProfileForm, EditUserProfileForm, UpgradeForm, ResetPasswordForm
from datawinners.accountmanagement.models import Organization, NGOUserProfile, PaymentDetails, MessageTracker, DataSenderOnTrialAccount
from django.contrib.auth.views import login, password_reset
from datawinners.main.utils import get_database_manager
from datawinners.project.models import get_all_projects
from django.utils.translation import ugettext as _
from datawinners.project.models import Project
from datawinners.utils import get_organization

def is_admin(f):
    def wrapper(*args, **kw):
        user = args[0].user
        if not user.groups.filter(name="NGO Admins").count() > 0:
            return HttpResponseRedirect(django_settings.HOME_PAGE)

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
            referer = django_settings.HOME_PAGE
            return HttpResponseRedirect(referer)
        return f(*args, **kw)

    return wrapper


def is_datasender(f):
    def wrapper(*args, **kw):
        user = args[0].user
        if user.get_profile().reporter:
            return HttpResponseRedirect(django_settings.DATASENDER_DASHBOARD)

        return f(*args, **kw)

    return wrapper


def is_datasender_allowed(f):
    def wrapper(*args, **kw):
        user = args[0].user
        if user.get_profile().reporter:
            projects = get_all_projects(get_database_manager(user), user.get_profile().reporter_id)
        else:
            projects = get_all_projects(get_database_manager(user))
        project_ids = [project.id for project in projects]
        project_id = kw['project_id']
        if not project_id in project_ids:
            return HttpResponseRedirect(django_settings.DATASENDER_DASHBOARD)

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


def is_expired(f):
    def wrapper(*args, **kw):
        request = args[0]
        user = request.user
        org = Organization.objects.get(org_id=user.get_profile().org_id)
        if org.is_expired():
            request.session.clear()
            return HttpResponseRedirect(django_settings.TRIAL_EXPIRED_URL)
        return f(*args, **kw)

    return wrapper


def is_trial(f):
    def wrapper(*args, **kw):
        user = args[0].user
        profile = user.get_profile()
        organization = Organization.objects.get(org_id=profile.org_id)
        if not organization.in_trial_mode:
            return HttpResponseRedirect(django_settings.HOME_PAGE)
        return f(*args, **kw)

    return wrapper


def registration_complete(request, user=None):
    return render_to_response('registration/registration_complete.html')


def custom_login(request, template_name, authentication_form):
    if request.user.is_authenticated():
        return HttpResponseRedirect(django_settings.LOGIN_REDIRECT_URL)
    else:
        try:
            return login(request, template_name=template_name, authentication_form=authentication_form)
        except AccountExpiredException:
            return HttpResponseRedirect(django_settings.TRIAL_EXPIRED_URL)


def _get_email_template_name_for_reset_password(language):
    return 'registration/password_reset_email_' + language + '.html'


def custom_reset_password(request):
    return password_reset(request,
        email_template_name=_get_email_template_name_for_reset_password(request.LANGUAGE_CODE),
        password_reset_form=ResetPasswordForm)


@login_required(login_url='/login')
@is_admin
def settings(request):
    if request.method == 'GET':
        organization = get_organization(request)
        organization_form = OrganizationForm(instance=organization)
        return render_to_response("accountmanagement/account/org_settings.html",
                {'organization_form': organization_form}, context_instance=RequestContext(request))

    if request.method == 'POST':
        organization = Organization.objects.get(org_id=request.POST["org_id"])
        organization_form = OrganizationForm(request.POST, instance=organization).update()
        message = "" if organization_form.errors else _('Settings have been updated successfully')
        return render_to_response("accountmanagement/account/org_settings.html",
                {'organization_form': organization_form, 'message': message}, context_instance=RequestContext(request))


def _associate_user_with_existing_project(manager, reporter_id):
    rows = get_all_projects(manager)
    for row in rows:
        project_id = row['value']['_id']
        project = Project.load(manager.database, project_id)
        project.data_senders.append(reporter_id)
        project.save(manager)


@login_required(login_url='/login')
@is_admin
def new_user(request):
    add_user_success = False
    if request.method == 'GET':
        profile_form = UserProfileForm()
        return render_to_response("accountmanagement/account/add_user.html", {'profile_form': profile_form},
            context_instance=RequestContext(request))

    if request.method == 'POST':
        manager = get_database_manager(request.user)
        org = get_organization(request)
        form = UserProfileForm(organization=org,data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            if not form.errors:
                user = User.objects.create_user(username, username, 'test123')
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                group = Group.objects.filter(name="Project Managers")
                user.groups.add(group[0])
                user.save()
                mobile_number = form.cleaned_data['mobile_phone']
                ngo_user_profile = NGOUserProfile(user=user, title=form.cleaned_data['title'],
                    mobile_phone=mobile_number,
                    org_id=org.org_id)
                ngo_user_profile.reporter_id = make_user_as_a_datasender(manager=manager, organization=org,
                    current_user_name=user.get_full_name(), mobile_number=mobile_number)
                ngo_user_profile.save()
                _associate_user_with_existing_project(manager, ngo_user_profile.reporter_id)
                reset_form = PasswordResetForm({"email": username})
                reset_form.is_valid()
                reset_form.save(email_template_name=_get_email_template_name_for_reset_password(request.LANGUAGE_CODE))
                form = UserProfileForm()
                add_user_success = True

        return render_to_response("accountmanagement/account/add_user.html",
                {'profile_form': form, 'add_user_success': add_user_success},
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
        if profile.mobile_phone == 'Not Assigned':
            profile.mobile_phone = ''
        form = EditUserProfileForm(data=dict(title=profile.title, first_name=profile.user.first_name,
            last_name=profile.user.last_name,
            username=profile.user.username,
            mobile_phone=profile.mobile_phone))
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
            ngo_user_profile.mobile_phone = form.cleaned_data['mobile_phone']

            ngo_user_profile.save()
            message = _('Profile has been updated successfully')
        return render_to_response("accountmanagement/profile/edit_profile.html", {'form': form, 'message': message},
            context_instance=RequestContext(request))


def trial_expired(request):
    return render_to_response("registration/trial_account_expired_message.html")


@is_admin
@is_trial
def upgrade(request):
    profile = request.user.get_profile()
    organization = get_organization(request)
    if request.method == 'GET':
        form = UpgradeForm()
        return render_to_response("registration/upgrade.html", {'organization': organization, 'profile': profile,
                                                                'form': form}, context_instance=RequestContext(request))
    if request.method == 'POST':
        form = UpgradeForm(request.POST)
        if form.is_valid():
            organization.in_trial_mode = False
            organization.save()

            invoice_period = form.cleaned_data['invoice_period']
            preferred_payment = form.cleaned_data['preferred_payment']
            payment_details = PaymentDetails.objects.model(organization=organization, invoice_period=invoice_period,
                preferred_payment=preferred_payment)
            payment_details.save()
            message_tracker = MessageTracker.objects.filter(organization=organization)
            if message_tracker.count() > 0:
                tracker = message_tracker[0]
                tracker.reset()
            DataSenderOnTrialAccount.objects.filter(organization=organization).delete()
            _send_upgrade_email(request.user, request.LANGUAGE_CODE)
            messages.success(request, _("upgrade success message"))
            return HttpResponseRedirect(django_settings.LOGIN_REDIRECT_URL)

        return render_to_response("registration/upgrade.html", {'organization': organization, 'profile': profile,
                                                                'form': form}, context_instance=RequestContext(request))


def _send_upgrade_email(user, language):
    subject = render_to_string('accountmanagement/upgrade_email_subject_' + language + '.txt')
    subject = ''.join(subject.splitlines()) # Email subject *must not* contain newlines
    body = render_to_string('accountmanagement/upgrade_email_' + language + '.html', {'name': user.first_name})
    email = EmailMessage(subject, body, EMAIL_HOST_USER, [user.email], [HNI_SUPPORT_EMAIL_ID])
    email.content_subtype = "html"
    email.send()
