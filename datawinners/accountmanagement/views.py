# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json
import datetime

from django.contrib.auth.decorators import login_required
from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.views import login, password_reset, password_reset_confirm
from django.utils.translation import ugettext as _, get_language, activate
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
from django.http import Http404
from django.contrib.auth import login as sign_in, logout
from django.utils.http import base36_to_int
from datawinners.accountmanagement.helper import get_all_users_for_organization
from mangrove.transport import TransportInfo
from rest_framework.authtoken.models import Token
from django.contrib.sites.models import Site

from datawinners.accountmanagement.decorators import is_admin, session_not_expired, is_not_expired, is_trial, valid_web_user, is_sms_api_user
from datawinners.accountmanagement.post_activation_events import make_user_as_a_datasender
from datawinners.settings import HNI_SUPPORT_EMAIL_ID, EMAIL_HOST_USER
from datawinners.main.database import get_database_manager
from mangrove.errors.MangroveException import AccountExpiredException
from datawinners.accountmanagement.forms import OrganizationForm, UserProfileForm, EditUserProfileForm, UpgradeForm, ResetPasswordForm
from datawinners.accountmanagement.models import Organization, NGOUserProfile, PaymentDetails, MessageTracker, \
    DataSenderOnTrialAccount, get_ngo_admin_user_profiles_for
from datawinners.project.models import get_all_projects, delete_datasenders_from_project
from datawinners.project.models import Project
from datawinners.utils import get_organization, _get_email_template_name_for_reset_password
from datawinners.activitylog.models import UserActivityLog
from datawinners.common.constant import CHANGED_ACCOUNT_INFO, ADDED_USER, DELETED_USERS
from datawinners.entity.helper import delete_datasender_for_trial_mode, \
    delete_datasender_users_if_any, delete_entity_instance
from datawinners.entity.import_data import send_email_to_data_sender
from mangrove.form_model.form_model import REPORTER


def registration_complete(request):
    return render_to_response('registration/registration_complete.html')


def registration_activation_complete(request):
    return HttpResponseRedirect(django_settings.LOGIN_REDIRECT_URL)


def custom_login(request, template_name, authentication_form):
    if request.user.is_authenticated():
        return HttpResponseRedirect(django_settings.LOGIN_REDIRECT_URL)
    else:
        try:
            response = login(request, template_name=template_name, authentication_form=authentication_form)
            if is_sms_api_user(request.user):
                logout(request)
            return response
        except AccountExpiredException:
            return HttpResponseRedirect(django_settings.TRIAL_EXPIRED_URL)


def custom_reset_password(request):
    return password_reset(request,
                          email_template_name=_get_email_template_name_for_reset_password(request.LANGUAGE_CODE),
                          password_reset_form=ResetPasswordForm)


@login_required
@session_not_expired
@is_admin
@is_not_expired
def settings(request):
    if request.method == 'GET':
        organization = get_organization(request)
        organization_form = OrganizationForm(instance=organization)

        return render_to_response("accountmanagement/account/org_settings.html",
                                  {'organization_form': organization_form}, context_instance=RequestContext(request))

    if request.method == 'POST':
        organization = Organization.objects.get(org_id=request.POST["org_id"])
        organization_form = OrganizationForm(request.POST, instance=organization).update()
        if organization_form.errors:
            message = ""
        else:
            message = _('Settings have been updated successfully')
            changed_data = organization_form.changed_data
            if len(changed_data) != 0:
                detail_dict = dict()
                current_lang = get_language()
                activate("en")
                for changed in changed_data:
                    label = u"%s" % organization_form.fields[changed].label
                    detail_dict.update({label: organization_form.cleaned_data.get(changed)})
                activate(current_lang)
                detail_as_string = json.dumps(detail_dict)
                UserActivityLog().log(request, action=CHANGED_ACCOUNT_INFO, detail=detail_as_string)

        return render_to_response("accountmanagement/account/org_settings.html",
                                  {'organization_form': organization_form, 'message': message},
                                  context_instance=RequestContext(request))


def associate_user_with_existing_project(manager, reporter_id):
    rows = get_all_projects(manager)
    for row in rows:
        project_id = row['value']['_id']
        questionnaire = Project.get(manager, project_id)
        questionnaire.associate_data_sender_to_project(manager, reporter_id)

@login_required
@session_not_expired
@is_admin
@is_not_expired
def new_user(request):
    add_user_success = False
    if request.method == 'GET':
        profile_form = UserProfileForm()
        return render_to_response("accountmanagement/account/add_user.html", {'profile_form': profile_form},
                                  context_instance=RequestContext(request))

    if request.method == 'POST':
        manager = get_database_manager(request.user)
        org = get_organization(request)
        form = UserProfileForm(organization=org, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            if not form.errors:
                user = User.objects.create_user(username, username, 'test123')
                user.first_name = form.cleaned_data['full_name']
                group = Group.objects.filter(name="Project Managers")
                user.groups.add(group[0])
                user.save()
                mobile_number = form.cleaned_data['mobile_phone']
                ngo_user_profile = NGOUserProfile(user=user, title=form.cleaned_data['title'],
                                                  mobile_phone=mobile_number,
                                                  org_id=org.org_id)
                ngo_user_profile.reporter_id = make_user_as_a_datasender(manager=manager, organization=org,
                                                                         current_user_name=user.get_full_name(),
                                                                         mobile_number=mobile_number, email=username)
                ngo_user_profile.save()
                associate_user_with_existing_project(manager, ngo_user_profile.reporter_id)
                reset_form = PasswordResetForm({"email": username})
                if reset_form.is_valid():
                    send_email_to_data_sender(reset_form.users_cache[0], request.LANGUAGE_CODE, request=request,
                                              type="created_user",organization=org)
                    name = form.cleaned_data.get("full_name")
                    form = UserProfileForm()
                    add_user_success = True
                    detail_dict = dict({"Name": name})
                    UserActivityLog().log(request, action=ADDED_USER, detail=json.dumps(detail_dict))

        return render_to_response("accountmanagement/account/add_user.html",
                                  {'profile_form': form, 'add_user_success': add_user_success},
                                  context_instance=RequestContext(request))


@valid_web_user
@is_admin
def users(request):
    if request.method == 'GET':
        org_id = request.user.get_profile().org_id
        users = get_all_users_for_organization(org_id)
        return render_to_response("accountmanagement/account/users_list.html", {'users': users},
                                  context_instance=RequestContext(request))


@valid_web_user
def edit_user(request):
    if request.method == 'GET':
        profile = request.user.get_profile()
        if profile.mobile_phone == 'Not Assigned':
            profile.mobile_phone = ''
        form = EditUserProfileForm(data=dict(title=profile.title, full_name=profile.user.first_name,
                                             username=profile.user.username,
                                             mobile_phone=profile.mobile_phone))
        return render_to_response("accountmanagement/profile/edit_profile.html", {'form': form},
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
        form = EditUserProfileForm(request.POST)
        message = ""
        if form.is_valid():
            _update_user_and_profile(request, form)
            
            message = _('Profile has been updated successfully')
        return render_to_response("accountmanagement/profile/edit_profile.html", {'form': form, 'message': message},
                                  context_instance=RequestContext(request))


def trial_expired(request):
    return render_to_response("registration/trial_account_expired_message.html")


@is_admin
@is_trial
def upgrade(request, token=None):
    profile = request.user.get_profile()
    organization = get_organization(request)
    if request.method == 'GET':
        form = UpgradeForm()
        organization_form = OrganizationForm(instance=organization)
        profile_form = EditUserProfileForm(data=dict(title=profile.title, full_name=profile.user.first_name,
                                             username=profile.user.username,
                                             mobile_phone=profile.mobile_phone))
        return render_to_response("registration/upgrade.html", {'organization': organization_form, 'profile': profile_form,
                                                                'form': form}, context_instance=RequestContext(request))
    if request.method == 'POST':
        form = UpgradeForm(request.POST)
        organization = Organization.objects.get(org_id=request.POST["org_id"])
        organization_form = OrganizationForm(request.POST, instance=organization).update()
        profile_form = EditUserProfileForm(request.POST)
        if form.is_valid() and organization_form.is_valid() and profile_form.is_valid():
            organization.save()

            invoice_period = form.cleaned_data['invoice_period']
            preferred_payment = form.cleaned_data['preferred_payment']

            payment_details = PaymentDetails.objects.model(organization=organization, invoice_period=invoice_period,
                                                           preferred_payment=preferred_payment)
            payment_details.save()
            message_tracker = MessageTracker(organization=organization, month=datetime.datetime.today())
            message_tracker.save()

            DataSenderOnTrialAccount.objects.filter(organization=organization).delete()
            _send_upgrade_email(request.user, request.LANGUAGE_CODE)
            _update_user_and_profile(request, profile_form)
            messages.success(request, _("upgrade success message"))
            if token:
                request.user.backend = 'django.contrib.auth.backends.ModelBackend'
                sign_in(request, request.user)
                Token.objects.get(pk=token).delete()
            return HttpResponseRedirect(django_settings.LOGIN_REDIRECT_URL)

        return render_to_response("registration/upgrade.html", {'organization': organization_form, 'profile': profile_form,
                                                                'form': form}, context_instance=RequestContext(request))


def _send_upgrade_email(user, language):
    subject = render_to_string('accountmanagement/upgrade_email_subject_' + language + '.txt')
    subject = ''.join(subject.splitlines()) # Email subject *must not* contain newlines
    site = Site.objects.get_current()
    body = render_to_string('accountmanagement/upgrade_email_' + language + '.html', {'username': user.first_name, 'site':site})
    email = EmailMessage(subject, body, EMAIL_HOST_USER, [user.email], [HNI_SUPPORT_EMAIL_ID])
    email.content_subtype = "html"
    email.send()


def user_activity_log_details(users_to_be_deleted):
    return "<br><br>".join(
        ("Name: " + user.get_full_name() + "<br>" + "Email: " + user.email) for user in users_to_be_deleted)


@login_required
@csrf_view_exempt
@csrf_response_exempt
@session_not_expired
@is_not_expired
def delete_users(request):
    if request.method == 'GET':
        raise Http404

    django_ids = request.POST.get("all_ids").split(";")
    all_ids = NGOUserProfile.objects.filter(user__in=django_ids).values_list('reporter_id', flat=True)
    manager = get_database_manager(request.user)
    organization = get_organization(request)
    transport_info = TransportInfo("web", request.user.username, "")
    ngo_admin_user_profile = get_ngo_admin_user_profiles_for(organization)[0]

    if ngo_admin_user_profile.reporter_id in all_ids:
        admin_full_name = ngo_admin_user_profile.user.first_name + ' ' + ngo_admin_user_profile.user.last_name
        messages.error(request, _("Your organization's account Administrator %s cannot be deleted") %
                                (admin_full_name), "error_message")
    else:
        detail = user_activity_log_details(User.objects.filter(id__in=django_ids))
        delete_entity_instance(manager, all_ids, REPORTER, transport_info)
        delete_datasenders_from_project(manager, all_ids)
        delete_datasender_users_if_any(all_ids, organization)

        if organization.in_trial_mode:
            delete_datasender_for_trial_mode(manager, all_ids, REPORTER)
        action = DELETED_USERS
        UserActivityLog().log(request, action=action, detail=detail)
        messages.success(request, _("User(s) successfully deleted."))

    return HttpResponse(json.dumps({'success': True}))


def custom_password_reset_confirm(request, uidb36=None, token=None, set_password_form=SetPasswordForm):
    response = password_reset_confirm(request, uidb36=uidb36, token=token, set_password_form=set_password_form,
                                      template_name='registration/datasender_activate.html')
    if request.method == 'POST' and type(response) == HttpResponseRedirect:
        try:
            uid_int = base36_to_int(uidb36)
            user = User.objects.get(id=uid_int)
        except (ValueError, User.DoesNotExist):
            return response
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        sign_in(request, user)
        redirect_url = django_settings.DATASENDER_DASHBOARD + '?activation=1' \
            if user.get_profile().reporter else django_settings.DASHBOARD
        return HttpResponseRedirect(redirect_url)
    return response

def _update_user_and_profile(request, form):
    user = User.objects.get(username=request.user.username)
    user.first_name = form.cleaned_data['full_name']
    user.save()
    ngo_user_profile = NGOUserProfile.objects.get(user=user)
    ngo_user_profile.title = form.cleaned_data['title']
    ngo_user_profile.mobile_phone = form.cleaned_data['mobile_phone']

    ngo_user_profile.save()