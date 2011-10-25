from datetime import datetime, timedelta
from django.core.mail.message import EmailMessage
from django.template import loader
from django.template.context import Context
from django.conf import settings
from datawinners.accountmanagement.models import NGOUserProfile, Organization

def send_deactivate_email():
    for organization in get_expired_account_list():
        create_email(get_creator(organization)).send()

def get_creator(organization):
    profiles = NGOUserProfile.objects.filter(org_id=organization.org_id)
    profiles.order_by('id')

    return profiles[0].user

def get_expired_account_list():
    organization_list=[]
    trial_organizations = Organization.objects.filter(in_trial_mode=True)

    for organization in trial_organizations:
        thirty_days_ago = datetime.today() - timedelta(days=30)
        thirty_one_days_ago = datetime.today() - timedelta(days=31)
        if organization.active_date is not None and organization.active_date < thirty_days_ago and organization.active_date > thirty_one_days_ago:
            organization_list.append(organization)

    return organization_list


def create_email(user):
    c=Context({ 'username': user.first_name +' '+ user.last_name})
    email_content = loader.get_template('deactivate/deactivate_email.html')
    email_subject = 'Please activate account email'

    msg = EmailMessage(email_subject, email_content.render(c), settings.EMAIL_HOST_USER, [user.email])
    msg.content_subtype = "html" 
    return msg

def get_creators(organizations):
    creators=[]
    for organization in organizations:
        creators.append(get_creator(organization))
    return creators

def send_email(users):
    for user in users:
       create_email(user).send()

