# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json
import datetime
from operator import itemgetter

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
from django.utils.translation import ugettext as _, get_language, activate, ugettext
from django.views.decorators.csrf import csrf_view_exempt, csrf_response_exempt
from django.http import Http404
from django.contrib.auth import login as sign_in, logout
from django.utils.http import base36_to_int
from rest_framework.authtoken.models import Token
from django.contrib.sites.models import Site

from datawinners.accountmanagement.helper import get_all_users_for_organization, update_corresponding_datasender_details
from datawinners.accountmanagement.localized_time import get_country_time_delta, convert_utc_to_localized
from datawinners.project.couch_view_helper import get_all_projects
from datawinners.project.templatetags.filters import friendly_name
from datawinners.search.datasender_index import update_datasender_index_by_id
from mangrove.transport import TransportInfo
from datawinners.accountmanagement.decorators import is_admin, session_not_expired, is_not_expired, is_pro_sms, \
    valid_web_user, is_sms_api_user, is_datasender, for_super_admin_only
from datawinners.accountmanagement.post_activation_events import make_user_as_a_datasender
from datawinners.settings import HNI_SUPPORT_EMAIL_ID, EMAIL_HOST_USER
from datawinners.main.database import get_database_manager
from mangrove.errors.MangroveException import AccountExpiredException
from datawinners.accountmanagement.forms import OrganizationForm, UserProfileForm, EditUserProfileForm, UpgradeForm, \
    ResetPasswordForm, UpgradeFormProSms
from datawinners.accountmanagement.models import Organization, NGOUserProfile, PaymentDetails, MessageTracker, \
    DataSenderOnTrialAccount, get_ngo_admin_user_profiles_for
from datawinners.project.models import delete_datasenders_from_project
from datawinners.utils import get_organization, _get_email_template_name_for_reset_password
from datawinners.activitylog.models import UserActivityLog
from datawinners.common.constant import CHANGED_ACCOUNT_INFO, ADDED_USER, DELETED_USERS, UPDATED_USER
from datawinners.entity.helper import delete_datasender_for_trial_mode, \
    delete_datasender_users_if_any, delete_entity_instance
from datawinners.entity.import_data import send_email_to_data_sender
from mangrove.form_model.form_model import REPORTER
from mangrove.form_model.project import Project
from datawinners.accountmanagement.registration_views import get_previous_page_language
from mangrove.datastore.user_permission import UserPermission, \
    get_user_permission, get_questionnaires_for_user, update_user_permission
from collections import OrderedDict
from django.db import transaction
import logging
datawinners_logger = logging.getLogger("datawinners")


def registration_complete(request):
    return render_to_response('registration/registration_complete.html')


def registration_activation_complete(request):
    request.session['activation_successful'] = True
    return HttpResponseRedirect(django_settings.LOGIN_REDIRECT_URL)


def custom_login(request, template_name, authentication_form, language=None):
    if language:
        request.session['django_language'] = language
        activate(language)
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


def _get_timezone_information(organization):
    timedelta = get_country_time_delta(organization.country)
    localized_time = convert_utc_to_localized(timedelta, datetime.datetime.utcnow())
    timedelta_as_string = "%s%.2d:%.2d" % (timedelta[0], timedelta[1], timedelta[2])
    return ugettext("GMT%s <span class='timezone-text'>  Now it is: %s</span>") % (
        timedelta_as_string, datetime.datetime.strftime(localized_time, "%H:%M"))


@login_required
@session_not_expired
@for_super_admin_only
@is_not_expired
def settings(request):
    if request.method == 'GET':
        organization = get_organization(request)
        organization_form = OrganizationForm(instance=organization)

        return render_to_response("accountmanagement/account/org_settings.html",
                                  {
                                      'organization_form': organization_form,
                                      'is_pro_sms': organization.is_pro_sms,
                                      'timezone_information': _get_timezone_information(organization),
                                      'current_lang': get_language()
                                  }, context_instance=RequestContext(request))

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
                                  {
                                      'organization_form': organization_form,
                                      'is_pro_sms': organization.is_pro_sms,
                                      'message': message,
                                      'timezone_information': _get_timezone_information(organization),
                                      'current_lang': get_language()
                                  },
                                  context_instance=RequestContext(request))


def associate_user_with_all_projects_of_organisation(manager, reporter_id):
    rows = get_all_projects(manager)
    for row in rows:
        make_user_data_sender_with_project(manager, reporter_id, row['value']['_id'])


def make_user_data_sender_with_project(manager, reporter_id, project_id):
    questionnaire = Project.get(manager, project_id)
    reporters_to_associate = [reporter_id]
    questionnaire.associate_data_sender_to_project(manager, reporters_to_associate)
    for data_senders_code in reporters_to_associate:
        update_datasender_index_by_id(data_senders_code, manager)


def associate_user_with_projects(manager, reporter_id, user_id, project_ids):
    make_user_data_sender_for_projects(manager, project_ids, reporter_id)
    UserPermission(manager, user_id, project_ids).save()


def make_user_data_sender_for_projects(manager, project_ids, reporter_id):
    for project_id in project_ids:
        make_user_data_sender_with_project(manager, reporter_id, project_id)


def activity_log_detail(name, role, questionnaires=None):
    detail = OrderedDict()
    detail["Name"] = name
    detail["Role"] = role
    if questionnaires:
        detail["Questionnaires & Polls"] = ",<br>".join(questionnaires)
    return json.dumps(detail)

@login_required
@session_not_expired
@is_admin
@is_not_expired
def new_user(request):
    org = get_organization(request)
    add_user_success = True
    manager = get_database_manager(request.user)
    if request.method == 'GET':
        profile_form = UserProfileForm()

        return render_to_response("accountmanagement/account/add_new_user.html", {'profile_form': profile_form,
                                                                                  'is_pro_sms': org.is_pro_sms,
                                                                                  'current_lang': get_language()
                                                                                  },
                                  context_instance=(RequestContext(request)))

    if request.method == 'POST':
        post_parameters = request.POST
        org = get_organization(request)
        form = UserProfileForm(organization=org, data=request.POST)
        errors = {}

        if form.is_valid():
            username = post_parameters['username']
            role = post_parameters['role']
            if not form.errors:
                sid = transaction.savepoint()
                user = User.objects.create_user(username, username, 'test123')
                user.first_name = post_parameters['full_name']
                group = Group.objects.filter(name=role)
                user.groups.add(group[0])
                user.save()
                mobile_number = post_parameters['mobile_phone']
                ngo_user_profile = NGOUserProfile(user=user, title=post_parameters['title'],
                                                  mobile_phone=mobile_number,
                                                  org_id=org.org_id)
                ngo_user_profile.reporter_id = make_user_as_a_datasender(manager=manager, organization=org,
                                                                         current_user_name=user.get_full_name(),
                                                                         mobile_number=mobile_number, email=username)
                ngo_user_profile.save()
                reset_form = PasswordResetForm({"email": username})

                name = post_parameters["full_name"]
                try:
                    if role == 'Extended Users':
                        associate_user_with_all_projects_of_organisation(manager, ngo_user_profile.reporter_id)
                        UserActivityLog().log(request, action=ADDED_USER, detail=activity_log_detail(name, friendly_name(role)))
                    elif role == 'Project Managers':
                        selected_questionnaires = post_parameters.getlist('selected_questionnaires[]')
                        selected_questionnaire_names = post_parameters.getlist('selected_questionnaire_names[]')
                        if selected_questionnaires is None:
                            selected_questionnaires = []
                        associate_user_with_projects(manager, ngo_user_profile.reporter_id, user.id,
                                                     selected_questionnaires)
                        UserActivityLog().log(request, action=ADDED_USER, detail=activity_log_detail(name, friendly_name(role), selected_questionnaire_names))
                        transaction.savepoint_commit(sid)

                except Exception as e:
                    transaction.savepoint_rollback(sid)
                    datawinners_logger.exception(e.message)
                    add_user_success = False


                if add_user_success and reset_form.is_valid():
                    send_email_to_data_sender(reset_form.users_cache[0], request.LANGUAGE_CODE, request=request,
                                              type="created_user", organization=org)

                    form = UserProfileForm()
                else:
                    add_user_success = False
        else:
            errors = form.errors
            add_user_success = False
            
        if len(request.user.groups.filter(name__in=["NGO Admins"])) < 1:
            current_user_type = "Administrator"
        else:
            current_user_type = "Account-Administrator"
        data = {"add_user_success": add_user_success, "errors": errors, "current_user": current_user_type}
        return HttpResponse(json.dumps(data), mimetype="application/json", status=201)

#TODO need to be removed when the flow is correctly working...
def roll_back_user_creation(user, reporter_id, role, organization):
    manager = get_database_manager(user)
    transport_info = TransportInfo("web", user.username, "")
    dissociate_user_as_datasender_with_projects(reporter_id, user, role, [])
    if organization.in_trial_mode:
        delete_datasender_for_trial_mode(manager, [reporter_id], REPORTER)
        
    delete_entity_instance(manager, [reporter_id], REPORTER, transport_info)
    delete_datasender_users_if_any([reporter_id], organization)
    user.delete()


@valid_web_user
@is_admin
def users(request):
    manager = get_database_manager(request.user)

    if request.method == 'GET':
        org_id = request.user.get_profile().org_id
        users = get_all_users_for_organization(org_id)
        organization = get_organization(request)
        questionnaire_map = dict()
        for user in users:
            questionnaires_for_user = get_questionnaires_for_user(user.user.id, get_database_manager(user.user))
            questionnaire_map.update({user.id: make_questionnaire_map(questionnaires_for_user)})

        return render_to_response("accountmanagement/account/users_list.html", {'current_user': request.user,
                                                                                'users': users,
                                                                                'questionnaire_map': questionnaire_map,
                                                                                'is_pro_sms': organization.is_pro_sms,
                                                                                'current_lang': get_language()},
                                  context_instance=RequestContext(request))


def make_questionnaire_map(questionnaires):
    questionnaires_for_user = list()
    for questionnaire in questionnaires:
        qmap = dict()
        qmap.update({'id': questionnaire['_id'], 'name': questionnaire['name']})
        questionnaires_for_user.append(qmap)

    return questionnaires_for_user


def get_user_profile(user_id):
    user = User.objects.get(id=user_id)
    if user is None:
        profile = user.get_profile()
        return profile
    return None


def trial_expired(request):
    return render_to_response("registration/trial_account_expired_message.html",
                              context_instance=RequestContext(request))


@for_super_admin_only
@is_pro_sms
def upgrade(request, token=None, account_type=None, language=None):
    if language:
        request.session['django_language'] = language
        activate(language)
    profile = request.user.get_profile()
    organization = get_organization(request)
    if request.method == 'GET':
        form = UpgradeForm() if not account_type else UpgradeFormProSms()
        organization_form = OrganizationForm(instance=organization)
        profile_form = EditUserProfileForm(organization=organization, reporter_id=profile.reporter_id,
                                           data=dict(title=profile.title, full_name=profile.user.first_name,
                                                     username=profile.user.username,
                                                     mobile_phone=profile.mobile_phone))
        return render_to_response("registration/upgrade.html",
                                  {'organization': organization_form, 'profile': profile_form,
                                   'form': form}, context_instance=RequestContext(request))
    if request.method == 'POST':
        role = request.user.groups.all()[0].name
        post_parameters = request.POST.copy()
        post_parameters['role'] = role
        form = UpgradeForm(post_parameters)
        organization = Organization.objects.get(org_id=post_parameters["org_id"])
        organization_form = OrganizationForm(post_parameters, instance=organization).update()
        profile_form = EditUserProfileForm(organization=organization, reporter_id=profile.reporter_id,
                                           data=post_parameters)
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
            _update_user_and_profile(profile_form, request.user.username)
            messages.success(request, _("upgrade success message"))
            if token:
                request.user.backend = 'django.contrib.auth.backends.ModelBackend'
                sign_in(request, request.user)
                Token.objects.get(pk=token).delete()
            return HttpResponseRedirect(django_settings.LOGIN_REDIRECT_URL)

        return render_to_response("registration/upgrade.html",
                                  {'organization': organization_form, 'profile': profile_form,
                                   'form': form}, context_instance=RequestContext(request))


def _send_upgrade_email(user, language):
    subject = render_to_string('accountmanagement/upgrade_email_subject_' + language + '.txt')
    subject = ''.join(subject.splitlines())  # Email subject *must not* contain newlines
    site = Site.objects.get_current()
    body = render_to_string('accountmanagement/upgrade_email_' + language + '.html',
                            {'username': user.first_name, 'site': site})
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
        messages.error(request, _("Your organization's account Administrator %s cannot be deleted") %
                       (ngo_admin_user_profile.user.first_name), "error_message")
    else:
        detail = user_activity_log_details(User.objects.filter(id__in=django_ids))
        delete_datasenders_from_project(manager, all_ids)
        delete_entity_instance(manager, all_ids, REPORTER, transport_info)
        delete_datasender_users_if_any(all_ids, organization)

        if organization.in_trial_mode:
            delete_datasender_for_trial_mode(manager, all_ids, REPORTER)
        action = DELETED_USERS
        UserActivityLog().log(request, action=action, detail=detail)
        messages.success(request, _("User(s) successfully deleted."))

    return HttpResponse(json.dumps({'success': True}))


def custom_password_reset_confirm(request, uidb36=None, token=None, set_password_form=SetPasswordForm,
                                  template_name='registration/datasender_activate.html'):
    response = password_reset_confirm(request, uidb36=uidb36, token=token, set_password_form=set_password_form,
                                      template_name=template_name)
    if request.method == 'POST' and type(response) == HttpResponseRedirect:
        try:
            uid_int = base36_to_int(uidb36)
            user = User.objects.get(id=uid_int)
        except (ValueError, User.DoesNotExist):
            return response
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        sign_in(request, user)
        redirect_url = django_settings.DATASENDER_DASHBOARD + '?activation=1' \
            if user.get_profile().reporter else django_settings.HOME_PAGE
        return HttpResponseRedirect(redirect_url)
    return response


def _update_user_and_profile(form, user_name, role=None):
    user = User.objects.get(username=user_name)
    user.first_name = form.cleaned_data['full_name']
    if role is not None:
        group = Group.objects.filter(name=role)
        user.groups.clear()
        user.groups.add(group[0])
    user.save()
    ngo_user_profile = NGOUserProfile.objects.get(user=user)
    ngo_user_profile.title = form.cleaned_data['title']
    old_phone_number = ngo_user_profile.mobile_phone
    ngo_user_profile.mobile_phone = form.cleaned_data['mobile_phone']

    ngo_user_profile.save()
    update_corresponding_datasender_details(user, ngo_user_profile, old_phone_number)


def dissociate_user_as_datasender_with_projects(reporter_id, user, previous_role, selected_questionnaires):
    manager = get_database_manager(user)

    if previous_role == 'Project Managers':
        user_permission = get_user_permission(user.id, manager)
        project_ids = user_permission.project_ids if user_permission else []
    elif previous_role == 'Extended Users':
        rows = get_all_projects(manager)
        project_ids = []
        for row in rows:
            project_ids.append(row['value']['_id'])

    remove_user_as_datasender_for_projects(manager, project_ids, selected_questionnaires, reporter_id)
    return


def remove_user_as_datasender_for_projects(manager, project_ids, selected_questionnaires, reporter_id):
    removed_questionnaires = list(set(project_ids) - set(selected_questionnaires))
    for questionnaire in removed_questionnaires:
        project = Project.get(manager, questionnaire)
        project.delete_datasender(manager, reporter_id)
        update_datasender_index_by_id(reporter_id, manager)


@valid_web_user
@is_datasender
def edit_user(request):
    if request.method == 'GET':
        profile = request.user.get_profile()
        if profile.mobile_phone == 'Not Assigned':
            profile.mobile_phone = ''
        org = get_organization(request)
        form = EditUserProfileForm(organization=org, reporter_id=profile.reporter_id,
                                   data=dict(title=profile.title, full_name=profile.user.first_name,
                                             username=profile.user.username,
                                             mobile_phone=profile.mobile_phone))
        return render_to_response("accountmanagement/profile/edit_profile.html",
                                  {'form': form, 'is_pro_sms': org.is_pro_sms},
                                  context_instance=RequestContext(request))
    if request.method == 'POST':
        post_parameter = request.POST.copy()
        post_parameter['role'] = request.user.groups.all()[0].name
        profile = request.user.get_profile()
        org = get_organization(request)

        form = EditUserProfileForm(organization=org, reporter_id=profile.reporter_id, data=post_parameter)
        message = ""
        if form.is_valid():
            _update_user_and_profile(form, request.user.username)

            message = _('Profile has been updated successfully')
        return render_to_response("accountmanagement/profile/edit_profile.html", {'form': form, 'message': message,
                                                                                  'is_pro_sms':org.is_pro_sms},
                                  context_instance=RequestContext(request))


@valid_web_user
@is_admin
def edit_user_profile(request, user_id=None):
    user = User.objects.get(id=user_id)
    current_user = request.user

    if user is None:
        data = {"errors": "User not found"}
        return HttpResponse(json.dumps(data), mimetype="application/json", status=404)
    if not current_user.has_higher_privileges_than(user):
        return HttpResponseRedirect(django_settings.ACCESS_DENIED_PAGE)
    else:
        profile = user.get_profile()
    if request.method == 'GET':
        if profile.mobile_phone == 'Not Assigned':
            profile.mobile_phone = ''
        org = get_organization(request)
        manager = get_database_manager(user)
        questionnaire_list = get_questionnaires_for_user(user.id, manager)
        questionnaire_map = make_questionnaire_map(questionnaire_list)
        form_data = dict(title=profile.title,
                         id=user_id,
                         full_name=profile.user.first_name,
                         username=profile.user.username,
                         mobile_phone=profile.mobile_phone,
                         role=user.groups.all()[0].name,
                         questionnaires=questionnaire_map)
        return render_to_response("accountmanagement/account/edit_user.html", {'form_data': json.dumps(form_data),
                                                                               'is_pro_sms': org.is_pro_sms,
                                                                               'current_lang': get_language()},
                                  context_instance=(RequestContext(request)))

    if request.method == 'POST':
        post_parameters = request.POST
        role = post_parameters['role']
        ngo_user = NGOUserProfile.objects.get(user=user)
        manager = get_database_manager(user)
        reporter_id = ngo_user.reporter_id
        previous_role = user.groups.all()[0].name
        org = get_organization(request)
        form = EditUserProfileForm(organization=org, reporter_id=profile.reporter_id, data=request.POST)
        message = ""
        _edit_user_success = False
        if form.is_valid():
            _update_user_and_profile(form, user.username, role)

            name = post_parameters["full_name"]

            if role == 'Project Managers':
                selected_questionnaires = post_parameters.getlist('selected_questionnaires[]')
                selected_questionnaire_names = post_parameters.getlist('selected_questionnaire_names[]')
                if selected_questionnaires is None or len(selected_questionnaires) < 1:
                    selected_questionnaires = []

                dissociate_user_as_datasender_with_projects(reporter_id, user, previous_role, selected_questionnaires)
                make_user_data_sender_for_projects(manager, selected_questionnaires, reporter_id)
                update_user_permission(manager, user_id=user.id, project_ids=selected_questionnaires)
                UserActivityLog().log(request, action=UPDATED_USER, detail=activity_log_detail(name, friendly_name(role), selected_questionnaire_names))
            elif role == 'Extended Users':
                if previous_role != 'Extended Users':
                    associate_user_with_all_projects_of_organisation(manager, reporter_id)
                    update_user_permission(manager, user_id=user.id, project_ids=[])
                UserActivityLog().log(request, action=UPDATED_USER, detail=activity_log_detail(name, friendly_name(role)))

            message = _('Profile has been updated successfully')
            _edit_user_success = True
        data = dict(edit_user_success=_edit_user_success,
                    errors=form.errors, message=message)
        return HttpResponse(json.dumps(data), mimetype="application/json", status=200)


@login_required
@session_not_expired
def access_denied(request):
    org = get_organization(request)
    return render_to_response("accountmanagement/account/access_denied.html", {'is_pro_sms': org.is_pro_sms,
                                                                               'current_lang': get_language()},
                              context_instance=(RequestContext(request)))
