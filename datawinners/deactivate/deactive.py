from django.core.mail.message import EmailMessage
from django.template import loader
from django.template.context import Context
from django.conf import settings
from datawinners.accountmanagement.models import NGOUserProfile, Organization

def send_deactivate_email():
    organizations = get_expired_trial_organizations_without_deactivate_email_sent()
    if not organizations:
        pass

    for organization in organizations:
        account_creator = get_creator(organization)
        if not account_creator:
            continue

        result = create_email(account_creator).send()
        if result:
            organization.is_deactivate_email_sent = True
            organization.save()

def get_creator(organization):
    profiles = NGOUserProfile.objects.filter(org_id=organization.org_id)
    profiles.order_by('id')

    return profiles[0].user if profiles else None

def get_expired_trial_organizations_without_deactivate_email_sent():
    organization_list=[]
    trial_organizations = Organization.objects.filter(in_trial_mode=True)

    for organization in trial_organizations:
        if organization.is_expired() and not organization.is_deactivate_email_sent:
            organization_list.append(organization)

    return organization_list


def create_email(user):
    msg = ''
    if user:
        c=Context({ 'username': user.first_name +' '+ user.last_name})
        email_content = loader.get_template('deactivate/deactivate_email.html')
        email_subject = 'Account Expired'

        msg = EmailMessage(email_subject, email_content.render(c), settings.EMAIL_HOST_USER, [user.email])
        msg.content_subtype = "html"
    return msg

def get_creators(organizations):
    creators=[]
    for organization in organizations:
        creators.append(get_creator(organization))
    return creators

def deactivate_expired_trial_account():
    organizations = get_expired_trial_organizations()
    if not organizations:
        pass

    for organization in organizations:
        organization.deactivate()

def get_expired_trial_organizations():
    trial_organizations = Organization.objects.filter(in_trial_mode=True, status='Activated')
    return [organization for organization in trial_organizations if organization.is_expired()]
