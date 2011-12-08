# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import datetime

from django.conf import settings
from django.contrib.auth.models import  User
from django.db import models
from django.template.defaultfilters import slugify

from datawinners.accountmanagement.organization_id_creator import OrganizationIdCreator

TEST_REPORTER_MOBILE_NUMBER = '0000000000'

def create_organization(org_details):
    organization = Organization(name=org_details.get('organization_name'),
                            sector=org_details.get('organization_sector'),
                            address=org_details.get('organization_address'),
                            city=org_details.get('organization_city'),
                            state=org_details.get('organization_state'),
                            country=org_details.get('organization_country'),
                            zipcode=org_details.get('organization_zipcode'),
                            office_phone=org_details.get('organization_office_phone'),
                            website=org_details.get('organization_website'),
                            org_id=OrganizationIdCreator().generateId())

    organization.settings =_configure_organization_settings(organization.name, organization.org_id)
    return organization

def create_trial_organization(org_details):
    organization = Organization(name=org_details.get('organization_name'),
                            sector=org_details.get('organization_sector'),
                            city=org_details.get('organization_city'),
                            country=org_details.get('organization_country'),
                            org_id=OrganizationIdCreator().generateId(),
                            in_trial_mode = True)
    
    organization.settings = _configure_organization_settings(organization.name, organization.org_id)
    return organization

class SMSC(models.Model):
    vumi_username = models.TextField()

    def __unicode__(self):
        return self.vumi_username
    
class OrgSettings(models.Model):
    in_trial_mode = models.BooleanField(default=False)
    active_date = models.DateTimeField(blank=True, null=True)
    is_deactivate_email_sent = models.BooleanField(False)
    document_store = models.TextField()
    sms_tel_number = models.TextField(unique=True, null=True)
    smsc = models.ForeignKey(SMSC, null=True,
                             blank=True)

    def get_organisation_sms_number(self):
        if self.in_trial_mode:
            return settings.TRIAL_ACCOUNT_PHONE_NUMBER
        return self.sms_tel_number

    def __unicode__(self):
        return self.document_store

class Organization(models.Model):
    name = models.TextField()
    sector = models.TextField()
    address = models.TextField()
    addressline2 = models.TextField(blank=True)
    city = models.TextField()
    state = models.TextField(blank=True)
    country = models.TextField()
    zipcode = models.TextField()
    office_phone = models.TextField(blank=True)
    website = models.TextField(blank=True)
    org_id = models.TextField(primary_key=True)
    settings = models.ForeignKey(OrgSettings, null=True)

    def is_expired(self, current_time = None):
        if not self.settings.in_trial_mode or self.settings.active_date is None:
            return False
        if current_time is None:
            current_time = datetime.datetime.now()
        diff_days = (current_time - self.settings.active_date).days
        return diff_days >= settings.EXPIRED_DAYS_FOR_TRIAL_ACCOUNT

    def get_message_tracker(self, date):
        message_tracker_tuple = MessageTracker.objects.get_or_create(organization=self, month=date)
        return message_tracker_tuple[0]

        
class DataSenderOnTrialAccount(models.Model):
    mobile_number = models.TextField(unique=True, primary_key=True)
    organization = models.ForeignKey(Organization)


class NGOUserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    title = models.TextField()
    org_id = models.TextField()
    office_phone = models.TextField(null=True, blank=True)
    mobile_phone = models.TextField(null=True, blank=True)
    skype = models.TextField(null=True)
    reporter_id = models.CharField(null=True, max_length=20)

    @property
    def reporter(self):
        return self.reporter_id is not None

class PaymentDetails(models.Model):
    organization = models.ForeignKey(Organization)
    invoice_period = models.TextField()
    preferred_payment = models.TextField()
    
class MessageTracker(models.Model):

    organization = models.ForeignKey(Organization)
    month = models.DateField()
    incoming_sms_count = models.IntegerField(default=0)
    outgoing_sms_count = models.IntegerField(default=0)

    def increment_incoming_message_count(self):
        self.incoming_sms_count += 1
        self.save()

    def increment_outgoing_message_count(self):
        self.outgoing_sms_count += 1
        self.save()

    def should_handle_message(self):
        if self.organization.settings.in_trial_mode:
            if (self.incoming_sms_count + self.outgoing_sms_count) > 100:
                return False

        return True

    def reset(self):
        self.incoming_sms_count = 0
        self.outgoing_sms_count = 0
        self.save()

    def __unicode__(self):
        return "organization : %s incoming messages: %d outgoing messages: %d" % (
        self.organization.name, self.incoming_sms_count, self.outgoing_sms_count)


def _configure_organization_settings(name, org_id):
    organization_setting = OrgSettings()
    organization_setting.document_store = slugify("%s_%s_%s" % ("HNI", name, org_id))
    return organization_setting
