# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import json
from datawinners.entity.helper import update_data_sender_from_trial_organization, put_email_information_to_entity
from datawinners.entity.import_data import send_email_to_data_sender
from datawinners.main.database import get_database_manager
from mangrove.datastore.entity import get_by_short_code, contact_by_short_code
from mangrove.errors.MangroveException import NumberNotRegisteredException
from mangrove.utils.types import is_empty
from mangrove.transport.repository.reporters import find_reporters_by_from_number
from datawinners.accountmanagement.models import Organization, NGOUserProfile,\
    get_data_senders_on_trial_account_with_mobile_number, DataSenderOnTrialAccount
from datawinners.utils import get_database_manager_for_org
from django.contrib.auth.models import User, Group
from mangrove.form_model.form_model import REPORTER, NAME_FIELD


def get_trial_account_user_phone_numbers():
    trial_orgs = Organization.objects.filter(account_type='Basic')
    phone_numbers = []
    for org in trial_orgs:
        profiles = NGOUserProfile.objects.filter(org_id=org.org_id)
        phone_numbers.extend([profile.mobile_phone for profile in profiles])
    return phone_numbers

def get_unique_mobile_number_validator(organization):
    if organization.in_trial_mode:
        return is_mobile_number_unique_for_trial_account
    return is_mobile_number_unique_for_paid_account

def is_mobile_number_unique_for_trial_account(org, mobile_number):
    return is_empty(get_data_senders_on_trial_account_with_mobile_number(org, mobile_number)) and mobile_number not in get_trial_account_user_phone_numbers()

def is_mobile_number_unique_for_paid_account(org, mobile_number, reporter_id=None):
    manager = get_database_manager_for_org(org)
    from mangrove.transport.repository.reporters import find_reporters_by_from_number
    try:
        registered_reporters = find_reporters_by_from_number(manager, mobile_number)
    except NumberNotRegisteredException:
        return True
    if len(registered_reporters) == 1 and registered_reporters[0].short_code == reporter_id:
        return True
    return False

def get_all_registered_phone_numbers_on_trial_account():
    return DataSenderOnTrialAccount.objects.values_list('mobile_number', flat=True)


def is_org_user(user):
    return user.groups.filter(name__in=["NGO Admins", "Project Managers"]).count() > 0

def get_all_users_for_organization(org_id):
    viewable_users = User.objects.exclude(groups__name__in=['Data Senders', 'SMS API Users']).values_list('id',
                                                                                                          flat=True)
    return NGOUserProfile.objects.filter(org_id=org_id, user__in=viewable_users)

def get_all_user_repids_for_org(org_id):
    users = get_all_users_for_organization(org_id)
    return [user.reporter_id for user in users]

def update_user_name_if_exists(email, new_name):
    try:
        user = User.objects.get(email=email)
        user.first_name = new_name
        user.save()
    except User.DoesNotExist as e:
        pass

def update_corresponding_datasender_details(user,ngo_user_profile,old_phone_number):
    manager = get_database_manager(user)
    reporter_entity = get_by_short_code(manager, ngo_user_profile.reporter_id, [REPORTER])
    current_phone_number = ngo_user_profile.mobile_phone
    reporter_entity.update_latest_data([('name',user.first_name),("mobile_number", current_phone_number)])

    organization = Organization.objects.get(org_id=ngo_user_profile.org_id)
    if organization.in_trial_mode:
        update_data_sender_from_trial_organization(old_phone_number,
                                                   current_phone_number, organization.org_id)


def create_web_users(org_id, reporter_details, language_code):
    duplicate_entries = {}
    [duplicate_entries.update({item[0]: item[1]}) for item in reporter_details.items() if
     [val for val in reporter_details.values()].count(item[1]) > 1]

    errors = []
    if len(duplicate_entries) > 0:
        content = json.dumps({'success': False, 'errors': errors, 'duplicate_entries': duplicate_entries})

    organization = Organization.objects.get(org_id=org_id)
    dbm = get_database_manager_for_org(organization)
    existent_email_addresses = User.objects.filter(email__in=reporter_details.values()).values('email')

    if len(existent_email_addresses) > 0:
        for duplicate_email in existent_email_addresses:
            errors.append("User with email %s already exists" % duplicate_email['email'])
        content = json.dumps({'success': False, 'errors': errors, 'duplicate_entries': duplicate_entries})
    if errors.__len__() == 0 and duplicate_entries.keys().__len__() == 0:
        for reporter_id, email in reporter_details.iteritems():
            reporter_entity = contact_by_short_code(dbm, reporter_id)
            reporter_email = email.lower()
            put_email_information_to_entity(dbm, reporter_entity, email=reporter_email)
            user = User.objects.create_user(reporter_email, reporter_email, 'test123')
            group = Group.objects.filter(name="Data Senders")[0]
            user.groups.add(group)
            user.first_name = reporter_entity.value(NAME_FIELD)
            user.save()
            profile = NGOUserProfile(user=user, org_id=org_id, title="Mr",
                                     reporter_id=reporter_id.lower())
            profile.save()

            send_email_to_data_sender(user, language_code, organization=organization)

        content = json.dumps({'success': True, 'message': "Users has been created"})
    return content


def get_org_id(request):
    return request.user.get_profile().org_id
