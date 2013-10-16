# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import datetime
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext
from django_countries import CountryField
from datawinners.settings import LIMIT_TRIAL_ORG_MESSAGE_COUNT, LIMIT_TRIAL_ORG_SUBMISSION_COUNT
from datawinners.accountmanagement.organization_id_creator import OrganizationIdCreator
from django.contrib.auth.models import User
from django.utils.translation import get_language
from datawinners.countrytotrialnumbermapping.models import Country
from django.template.context import Context
from django.core.mail.message import EmailMessage
from django.template import loader
from datawinners.accountmanagement.utils import get_email_detail_by_type

TEST_REPORTER_MOBILE_NUMBER = '0000000000'


class Organization(models.Model):
    name = models.TextField()
    sector = models.TextField()
    address = models.TextField()
    addressline2 = models.TextField(blank=True)
    city = models.TextField()
    state = models.TextField(blank=True)
    country = CountryField()
    zipcode = models.TextField()
    office_phone = models.TextField(blank=True)
    website = models.TextField(blank=True)
    org_id = models.TextField(primary_key=True)
    in_trial_mode = models.BooleanField(default=False)
    active_date = models.DateTimeField(blank=True, null=True)
    is_deactivate_email_sent = models.BooleanField(False)
    status = models.CharField(null=True, max_length=20, default='Activated')
    status_changed_datetime = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return unicode(self.name + "(" + self.org_id + ")")

    def country_name(self):
        return ugettext(self.country.name)

    def is_expired(self, current_time=None):
        if not self.in_trial_mode or self.active_date is None:
            return False
        if current_time is None:
            current_time = datetime.datetime.now()
        active_date = self.status_changed_datetime if self.status_changed_datetime and self.status == 'Activated'\
            else self.active_date
        return (current_time - relativedelta(years=settings.TRIAL_PERIOD_IN_YEAR)) >= active_date

    @classmethod
    def create_organization(cls, org_details):
        organization = Organization(name=org_details.get('organization_name'),
                                    sector=org_details.get('organization_sector'),
                                    address=org_details.get('organization_address'),
                                    addressline2=org_details.get('organization_addressline2'),
                                    city=org_details.get('organization_city'),
                                    state=org_details.get('organization_state'),
                                    country=org_details.get('organization_country'),
                                    zipcode=org_details.get('organization_zipcode'),
                                    office_phone=org_details.get('organization_office_phone'),
                                    website=org_details.get('organization_website'),
                                    org_id=OrganizationIdCreator().generateId()
        )
        organization._configure_organization_settings()
        return organization

    @classmethod
    def create_trial_organization(cls, org_details):
        organization = Organization(name=org_details.get('organization_name'),
                                    sector=org_details.get('organization_sector'),
                                    city=org_details.get('organization_city'),
                                    country=org_details.get('organization_country'),
                                    org_id=OrganizationIdCreator().generateId(),
                                    in_trial_mode=True
        )
        organization._configure_organization_settings()
        return organization

    def has_exceeded_message_limit(self):
        if self.in_trial_mode and self._has_exceeded_limit_for_trial_account():
            return True
        return False

    def has_exceeded_submission_limit(self):
        if self.in_trial_mode and self._has_exceeded_submission_limit_for_trial_account():
            return True
        return False

    def increment_sms_api_usage_count(self):
        current_month = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, 1)
        message_tracker = self._get_message_tracker(current_month)
        message_tracker.increment_sms_api_usage_count()

    def increment_all_message_count(self):
        current_month = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, 1)
        message_tracker = self._get_message_tracker(current_month)
        message_tracker.increment_incoming_message_count_by(1)
        message_tracker.increment_outgoing_message_count_by(1)

    def increment_all_message_count_by(self, incoming_count, outgoing_count):
        current_month = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, 1)
        message_tracker = self._get_message_tracker(current_month)
        message_tracker.increment_incoming_message_count_by(incoming_count)
        message_tracker.increment_outgoing_message_count_by(outgoing_count)

    def increment_message_count_for(self, **kwargs):
        current_month = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, 1)
        message_tracker = self._get_message_tracker(current_month)
        for field_name, count in kwargs.items():
            current_count = getattr(message_tracker, field_name)
            setattr(message_tracker, field_name, count + current_count)
        message_tracker.save()

    #TODO Should be removed??
    def _configure_organization_settings(self):
        from datawinners.utils import generate_document_store_name

        organization_setting = OrganizationSetting()
        organization_setting.organization = self
        self.organization_setting = organization_setting
        organization_setting.document_store = generate_document_store_name(self.name, self.org_id)
        return organization_setting

    def _get_message_tracker(self, date):
        return MessageTracker.objects.get_or_create(organization=self, month=date)[0]

    def _get_all_message_trackers(self):
        return MessageTracker.objects.filter(organization=self)

    def get_total_message_count(self):
        message_trackers = self._get_all_message_trackers()
        return sum([message_tracker.total_messages() for message_tracker in message_trackers])

    def get_total_submission_count(self):
        message_trackers = self._get_all_message_trackers()
        return sum([message_tracker.total_monthly_incoming_messages() for message_tracker in message_trackers])

    def _has_exceeded_limit_for_trial_account(self):
        return self.get_total_message_count() >= LIMIT_TRIAL_ORG_MESSAGE_COUNT

    def _has_exceeded_submission_limit_for_trial_account(self):
        return self.get_total_submission_count() >= LIMIT_TRIAL_ORG_SUBMISSION_COUNT

    def get_phone_country_code(self):
        criteria = dict({"country_name_%s" % get_language(): self.country_name()})
        try:
            current_country = Country.objects.filter(**criteria)[0]
            return current_country.country_code if current_country else None
        except Exception:
            return None

    def tel_number(self):
        organization_setting = OrganizationSetting.objects.get(organization=self)
        return organization_setting.get_organisation_sms_number()[0]

    def purge_all_data(self):
        User.objects.filter(ngouserprofile__org_id=self.org_id).delete()
        NGOUserProfile.objects.filter(org_id=self.org_id).delete()
        self.delete()

    def deactivate(self):
        self.get_related_users().update(is_active=False)
        self.status = 'Deativated'
        self.save()

    def get_related_users(self):
        return User.objects.filter(ngouserprofile__org_id=self.org_id)

    def send_mail_to_organization_creator(self, email_type):
        users = self.get_related_users().filter(groups__name__in=["NGO Admins", "Project Managers"])
        for user in users:
            email_subject, email_template, sender = get_email_detail_by_type(email_type)

            c = Context({ 'username': user.first_name +' '+ user.last_name, 'organization':self})
            email_content = loader.get_template('email/%s_%s.html' % (email_template, ugettext("en"),))

            msg = EmailMessage(email_subject, email_content.render(c), sender or settings.EMAIL_HOST_USER, [user.email])
            msg.content_subtype = "html"
            msg.send()

    @classmethod
    def get_all_trial_organizations(cls, active_date__contains=None):
        if active_date__contains:
            return cls.objects.filter(in_trial_mode=True,status_changed_datetime__contains=active_date__contains)
        return cls.objects.filter(in_trial_mode=True)

def get_data_senders_on_trial_account_with_mobile_number(mobile_number):
    return DataSenderOnTrialAccount.objects.filter(mobile_number=mobile_number)


class DataSenderOnTrialAccount(models.Model):
    mobile_number = models.TextField(unique=True, primary_key=True)
    organization = models.ForeignKey(Organization)


def get_ngo_admin_user_profiles_for(organization):
    user_profiles = NGOUserProfile.objects.filter(org_id=organization.org_id)
    return [user_profile for user_profile in user_profiles if
            user_profile.user.groups.filter(name="NGO Admins")]


class NGOUserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    title = models.TextField()
    org_id = models.TextField()
    mobile_phone = models.TextField()
    reporter_id = models.CharField(null=True, max_length=20)

    @property
    def reporter(self):
        user = User.objects.get(email=self.user)
        return True if user.groups.filter(name="Data Senders").count() else False


class PaymentDetails(models.Model):
    organization = models.ForeignKey(Organization)
    invoice_period = models.TextField()
    preferred_payment = models.TextField()


class SMSC(models.Model):
    vumi_username = models.TextField()

    def __unicode__(self):
        return self.vumi_username


class OutgoingNumberSetting(models.Model):
    phone_number = models.CharField(unique=True, max_length=30,
                                    help_text='Number to be used for sms originating in DataWinners, like broadcasts and reminders')
    smsc = models.ForeignKey(SMSC, null=True, on_delete=models.SET_NULL,
                             help_text='SMS Center to be used to for sending outgoing message.')

    def __unicode__(self):
        return "%s: %s" % (self.phone_number, self.smsc.vumi_username)


class OrganizationSetting(models.Model):
    organization = models.ForeignKey(Organization, unique=True)
    document_store = models.TextField()
    sms_tel_number = models.TextField(unique=True, null=True,
                                      help_text='Phone numbers registered to the organization for sending in messages.')
    outgoing_number = models.ForeignKey(OutgoingNumberSetting, null=True, on_delete=models.SET_NULL,
                                        help_text='Number to be used for outgoing messages.')

    def get_organisation_sms_number(self):
        if self._get_organization().in_trial_mode:
            return settings.TRIAL_ACCOUNT_PHONE_NUMBER
        return [number.strip() for number in self.sms_tel_number.split(',')] if self.sms_tel_number is not None else [
            '']

    def _get_organization(self):
        return self.organization

    def __unicode__(self):
        return self.organization.name


class MessageTracker(models.Model):
    organization = models.ForeignKey(Organization)
    month = models.DateField()
    sms_api_usage_count = models.IntegerField(default=0)
    incoming_sms_count = models.IntegerField(default=0)
    sms_registration_count = models.IntegerField(default=0)
    incoming_web_count = models.IntegerField(default=0)
    incoming_sp_count = models.IntegerField(default=0)
    outgoing_sms_count = models.IntegerField(default=0)

    def increment_incoming_message_count_by(self, count):
        self.incoming_sms_count += count
        self.save()

    def increment_outgoing_message_count_by(self, count):
        self.outgoing_sms_count += count
        self.save()

    def increment_sms_api_usage_count(self):
        self.sms_api_usage_count += 1
        self.save()

    def outgoing_message_count(self):
        return self.sms_api_usage_count + self.outgoing_sms_count

    def total_messages(self):
        return self.outgoing_message_count() + self.incoming_sms_count

    def combined_total_messages(self):
        msg_trackers = MessageTracker.objects.filter(organization=self.organization_id, month__lt=self.month)
        total_msg = self.total_messages()
        for msg_tracker in msg_trackers:
            total_msg += msg_tracker.total_messages()
        return total_msg

    def total_monthly_incoming_messages(self):
        return self.incoming_sms_count + self.incoming_sp_count + self.incoming_web_count - self.sms_registration_count

    def reset(self):
        self.incoming_sms_count = 0
        self.outgoing_sms_count = 0
        self.incoming_web_count = 0
        self.incoming_sp_count = 0
        self.sms_api_usage_count = 0
        self.save()

    def total_incoming_in_total(self):
        msg_trackers = MessageTracker.objects.filter(organization=self.organization_id, month__lt=self.month)
        total_incoming = self.total_monthly_incoming_messages()
        for msg_tracker in msg_trackers:
            total_incoming += msg_tracker.total_monthly_incoming_messages()
        return total_incoming


    def __unicode__(self):
        return "organization : %s incoming messages: %d outgoing messages: %d" % (
            self.organization.name, self.incoming_sms_count, self.outgoing_sms_count)
