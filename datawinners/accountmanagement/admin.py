# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import datetime
import logging

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.core.exceptions import ValidationError
from django.forms import CharField
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django_digest.models import PartialDigest
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.contrib.admin.views.main import ChangeList
from datawinners.common.admin.utils import get_text_search_filter, get_admin_panel_filter
from datawinners.project.submission.export import export_to_new_excel

from datawinners.search.index_utils import get_elasticsearch_handle
from forms import forms
from datawinners.accountmanagement.models import OrganizationSetting, SMSC, PaymentDetails, MessageTracker, Organization, NGOUserProfile, OutgoingNumberSetting
from mangrove.form_model.field import ExcelDate
from mangrove.utils.types import is_empty, is_not_empty
from datawinners.countrytotrialnumbermapping.models import Country, Network
from datawinners.utils import get_database_manager_for_org
from datawinners.feeds.database import feeds_db_for
from django.db.models import Q


admin.site.disable_action('delete_selected')


class DatawinnerAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class OrganizationSettingAdmin(DatawinnerAdmin):
    list_display = ('organization_name', 'organization_id', 'type', 'payment_details', 'activation_date', 'admin_email')
    fields = ('sms_tel_number', 'outgoing_number')
    search_fields = ['organization__name','organization__org_id']
    ordering = ('-organization__active_date',)

    def organization_name(self, obj):
        return obj.organization.name

    organization_name.admin_order_field = "organization__name"

    def _get_ngo_admin(self, organization_setting):
        user_profiles = NGOUserProfile.objects.filter(org_id=organization_setting.organization.org_id)
        admin_users = [x.user for x in user_profiles if x.user.groups.filter(name="NGO Admins")]
        #right now there is only one ngo admin
        return admin_users[0] if is_not_empty(admin_users) else NullAdmin()

    def admin_email(self, obj):
        return self._get_ngo_admin(obj).email

    def organization_id(self, obj):
        return obj.organization.org_id

    organization_id.admin_order_field = "organization__org_id"

    def payment_details(self, obj):
        organization = obj.organization
        payment_details = PaymentDetails.objects.filter(organization=organization)
        if not is_empty(payment_details):
            return payment_details[0].preferred_payment

        return "--"

    def type(self, obj):
        return obj.organization.account_type

    type.admin_order_field = 'organization__account_type'

    def activation_date(self, obj):
        return obj.organization.active_date if obj.organization.active_date is not None else '--'

    activation_date.admin_order_field = "organization__active_date"


    activation_date.short_description = "Created on"


class MessageTrackerAdmin(DatawinnerAdmin):
    list_display = ("organization_name", "organization_id","type", "month", "combined_total_incoming",
                    "total_incoming_per_month", "total_messages", "total_outgoing_messages", "outgoing_sms_count","outgoing_sms_charged_count",
                    "sent_reminders_count","sent_reminders_charged_count", "send_message_count","send_message_charged_count",  "sms_api_usage_count","sms_api_usage_charged_count", "sms_submission", "incoming_sp_count",
                    "incoming_web_count", "sms_registration_count")

    search_fields = ['organization__name', 'organization__org_id', 'month']
    ordering = ('-month',)

    def __init__(self, *args, **kwargs):
        super(MessageTrackerAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None,)

    def organization_name(self, obj):
        return obj.organization.name
    organization_name.short_description = mark_safe('Organisation<br/>name')

    def type(self,obj):
        return obj.organization.account_type


    def organization_id(self, obj):
        return obj.organization.org_id
    organization_id.short_description = mark_safe('Organisation<br/>ID')

    def combined_total_incoming(self, obj):
        return obj.total_incoming_in_total()
    combined_total_incoming.short_description = mark_safe('Total<br/>incoming<br/>Submissions<br/>(In total)')

    def total_incoming_per_month(self, obj):
        return obj.total_monthly_incoming_messages()
    total_incoming_per_month.short_description = mark_safe('Total<br/>Incoming<br/>Submissions<br/>')

    def current_month(self, obj):
        return datetime.datetime.strftime(obj.month, "%m-%Y")
    current_month.short_description = "Month"

    def total_outgoing_messages(self, obj):
        return obj.outgoing_message_count()
    total_outgoing_messages.short_description = mark_safe('Outgoing Charged SMS:<br/>Total')


    def total_messages(self, obj):
        return obj.total_messages()
    total_messages.short_description = mark_safe('Total SMS<br/>(incoming<br/>and<br/>outgoing)')

    def combined_total_messages(self, obj):
        return obj.combined_total_messages()
    combined_total_messages.short_description = mark_safe('Total SMS<br/>(in total)')

    def sms_submission(self, obj):
        return obj.incoming_sms_count - obj.sms_registration_count
    sms_submission.short_description = mark_safe('SMS<br/>Submissions')

    def export_message_tracker_details_to_excel(modeladmin, request, query_set):
        headers = ["Organization Name", "Organization Id","Type", "Month", "Total Incoming Submissions (In total)", "Total Incoming Submissions",
                   "Total SMS (incoming and outgoing)", "Outgoing Charged SMS: Total", "Outgoing SMS: Auto Reply", "Outgoing Charged SMS: Auto Reply",
                   "Outgoing SMS: Reminders", "Outgoing Charged SMS: Reminders", "Outgoing SMS: Send Message", "Outgoing Charged SMS: Send Message",
                   "Outgoing SMS: API", "Outgoing Charged SMS: API", "SMS Submissions", "SP Submissions", "Web Submissions", "SMS Subject Registration"]
        list = []

        textSearchFilter = get_text_search_filter(request.GET,MessageTrackerAdmin.search_fields)
        adminPanelFilter = get_admin_panel_filter(request.GET)

        filteredSms = MessageTracker.objects.all().filter(Q(**adminPanelFilter) & (textSearchFilter))
        for messageTracker in filteredSms:
            sms_tracker_month = ExcelDate(datetime.datetime.combine(messageTracker.month, datetime.datetime.min.time()),
                                          'dd.mm.yyyy') if messageTracker.month else None

            list.append([modeladmin.organization_name(messageTracker), modeladmin.organization_id(messageTracker),
                         modeladmin.type(messageTracker),
                         sms_tracker_month, messageTracker.total_incoming_in_total(),
                         messageTracker.total_monthly_incoming_messages(),
                         messageTracker.total_messages(), messageTracker.outgoing_message_count(),
                         messageTracker.outgoing_sms_count, messageTracker.outgoing_sms_charged_count,
                         messageTracker.sent_reminders_count, messageTracker.sent_reminders_charged_count,
                         messageTracker.send_message_count,
                         messageTracker.send_message_charged_count, messageTracker.sms_api_usage_count,
                         messageTracker.sms_api_usage_charged_count,
                         modeladmin.sms_submission(messageTracker), messageTracker.incoming_sp_count,
                         messageTracker.incoming_web_count, messageTracker.sms_registration_count])

        response = export_to_new_excel(headers, list, 'tracker_list')
        return response

    actions = [export_message_tracker_details_to_excel]


class OrganizationChangeList(ChangeList):
    def get_query_set(self):
        if not self.params.get("q", ""):
            return super(OrganizationChangeList, self).get_query_set()

        from django.db import connection
        cursor = connection.cursor()
        query = """Select array_agg(DISTINCT o.org_id) from accountmanagement_organization o
            inner join accountmanagement_ngouserprofile p on p.org_id = o.org_id
            inner join auth_user u on u.id = p.user_id inner join auth_user_groups ug on ug.user_id = u.id
            inner join auth_group g on ug.group_id = g.id and g.name = %s  """
        params = ["NGO Admins"]

        for index, keyword in enumerate(self.params.get("q").split()):
            from django_countries.countries import COUNTRIES
            codes = ["'" + code + "'" for code, name in COUNTRIES if unicode(name).lower().find(keyword.lower()) != -1 ]
            country_codes = ', '.join(codes) if len(codes) else "''"
            query += "and " if index else "where"
            query += " (o.country in (%s) " % country_codes
            query += """OR  u.email ilike %s OR u.first_name||u.last_name ilike %s OR o.name ilike %s
                OR p.mobile_phone ilike %s OR o.address||o.addressline2||o.city||o.zipcode||o.state ilike %s
                OR o.office_phone ilike %s OR o.website ilike %s OR o.org_id ilike %s
                OR to_char(o.active_date, 'YYYY-MM-DD HH:MI:SS') ilike %s) """

            params.extend(["%" + keyword + "%"] * 9)

        cursor.execute(query, params)
        org_ids = cursor.fetchone()[0]
        qs = Organization.objects.filter(org_id__in=org_ids or [])

        if self.order_field:
            qs = qs.order_by('%s%s' % ((self.order_type == 'desc' and '-' or ''), self.order_field))
        else:
            qs = qs.order_by('-active_date')
        return qs


class OrganizationChangeList(ChangeList):
    def get_query_set(self):
        if not self.params.get("q", ""):
            return super(OrganizationChangeList, self).get_query_set()

        from django.db import connection
        cursor = connection.cursor()
        query = """Select array_agg(DISTINCT o.org_id) from accountmanagement_organization o
            inner join accountmanagement_ngouserprofile p on p.org_id = o.org_id
            inner join auth_user u on u.id = p.user_id inner join auth_user_groups ug on ug.user_id = u.id
            inner join auth_group g on ug.group_id = g.id and g.name = %s  """
        params = ["NGO Admins"]

        for index, keyword in enumerate(self.params.get("q").split()):
            from django_countries.countries import COUNTRIES
            codes = ["'" + code + "'" for code, name in COUNTRIES if unicode(name).lower().find(keyword.lower()) != -1 ]
            country_codes = ', '.join(codes) if len(codes) else "''"
            query += "and " if index else "where"
            query += " (o.country in (%s) " % country_codes
            query += """OR  u.email ilike %s OR u.first_name||u.last_name ilike %s OR o.name ilike %s
                OR p.mobile_phone ilike %s OR o.address||o.addressline2||o.city||o.zipcode||o.state ilike %s
                OR o.office_phone ilike %s OR o.website ilike %s OR o.org_id ilike %s
                OR to_char(o.active_date, 'YYYY-MM-DD HH:MI:SS') ilike %s) """

            params.extend(["%" + keyword + "%"] * 9)

        cursor.execute(query, params)
        org_ids = cursor.fetchone()[0]
        qs = Organization.objects.filter(org_id__in=org_ids or [])

        if self.order_field:
            qs = qs.order_by('%s%s' % ((self.order_type == 'desc' and '-' or ''), self.order_field))
        else:
            qs = qs.order_by('-active_date')
        return qs


class OrganizationAdmin(DatawinnerAdmin):
    list_display = (
        'name', 'org_id', 'complete_address', 'office_phone', 'website', 'paid', 'active_date', 'admin_name',
        'admin_email', 'admin_mobile_number', 'sms_api_users', 'status')
    actions = ['deactivate_organizations', 'activate_organizations', 'delete_organizations']
    search_fields = ['name', 'address', 'addressline2', 'city', 'zipcode', 'state', 'office_phone', 'website']
    ordering = ('-active_date',)

    def get_changelist(self, request, **kwargs):
        return OrganizationChangeList

    def get_query_set(self, request, queryset, search_term):
        queryset, use_distinct = super(OrganizationAdmin, self).get_search_results(request, queryset, search_term)
        if search_term:
            queryset = queryset.filter(ngouserprofile__title__icontains=search_term)
        return queryset, use_distinct

    def deactivate_organizations(modeladmin, request, queryset):
        queryset.exclude(status__in=['Deactivated','Pending Activation']).update(status='Deactivated',
                                                      status_changed_datetime=datetime.datetime.now())
        messages.success(request, _('The accounts selected have been deactivated successfully.'))
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        orgs_id = Organization.objects.filter(org_id__in=selected).exclude(status='Pending Activation').\
            values_list('org_id', flat=True)
        User.objects.filter(ngouserprofile__org_id__in=orgs_id).update(is_active=False)

    deactivate_organizations.short_description = "Deactivate accounts"

    def activate_organizations(modeladmin, request, queryset):
        queryset.exclude(status__in=['Activated','Pending Activation']).update(status='Activated', status_changed_datetime=datetime.datetime.now())
        messages.success(request, _('The accounts selected have been activated successfully.'))
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        orgs_id = Organization.objects.filter(org_id__in=selected).exclude(status='Pending Activation').\
            values_list('org_id', flat=True)
        User.objects.filter(ngouserprofile__org_id__in=orgs_id).update(is_active=True)

    activate_organizations.short_description = "Activate accounts"

    def delete_organizations(modeladmin, request, queryset):
        orgs = queryset.filter(status__in=['Deactivated', "Pending Activation"])
        for organization in orgs:
            dbm = get_database_manager_for_org(organization)
            organization.purge_all_data()
            del dbm.server[dbm.database_name]
            feed_database_name = "feed_" + dbm.database_name
            feed_dbm = feeds_db_for(feed_database_name)
            del feed_dbm.server[feed_database_name]
            es = get_elasticsearch_handle()
            try:
                es.delete_index(dbm.database_name)
            except Exception as e:
                logging.info("Could not delete index " + str(e.message))

    delete_organizations.short_description = "Delete accounts"

    class Media:
        css = {"all": ("/media/css/plugins/jqueryUI/jquery-ui-1.8.13.custom.css",)}
        js = ("/media/javascript/jquery.js", "/media/javascript/jqueryUI/jquery-ui-1.8.13.custom.min.js",)

    def sms_api_users(self, organization):
        user_profiles = NGOUserProfile.objects.filter(org_id=organization.org_id)
        return " , ".join([x.user.username for x in user_profiles if x.user.groups.filter(name="SMS API Users")])

    def paid(self, obj):
        return "No" if obj.in_trial_mode else "Yes"

    def _get_ngo_admin(self, organization):
        user_profiles = NGOUserProfile.objects.filter(org_id=organization.org_id)
        admin_users = [x.user for x in user_profiles if x.user.groups.filter(name="NGO Admins")]
        #right now there is only one ngo admin
        return admin_users[0] if is_not_empty(admin_users) else NullAdmin()

    def admin_email(self, obj):
        return self._get_ngo_admin(obj).email

    def admin_office_phone(self, obj):
        admin_user = self._get_ngo_admin(obj)
        return admin_user.get_profile().office_phone

    def admin_mobile_number(self, obj):
        admin_user = self._get_ngo_admin(obj)
        return admin_user.get_profile().mobile_phone

    def admin_name(self, obj):
        admin_user = self._get_ngo_admin(obj)
        return admin_user.first_name

    def complete_address(self, obj):
        complete_address = [obj.address, obj.addressline2, obj.city, obj.zipcode, obj.state, obj.country_name()]
        return ", ".join([element for element in complete_address if is_not_empty(element)])

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('status',)
        return self.readonly_fields

    def payment_period(self, obj):
        payment_period_label = {"pay_monthly":"1 month","half_yearly":"6 months","yearly":"12 months"}
        organization = obj
        payment_period = PaymentDetails.objects.filter(organization=organization)
        if not is_empty(payment_period):
            return payment_period_label[payment_period[0].invoice_period] + ' / ' + payment_period[0].preferred_payment

        return "--"


class NullAdmin:
    def __init__(self):
        self.email = ''
        self.mobile_phone = ''
        self.office_phone = ''
        self.first_name = ''

    def get_profile(self):
        return self


class CountryAdmin(admin.ModelAdmin):
    ordering = ('country_name_en',)
    list_display = ('country_name_en', 'country_code')


class NetworkAdmin(admin.ModelAdmin):
    ordering = ('network_name',)
    list_display = ('network_name', 'trial_sms_number', 'country_name')
    filter_horizontal = ['country']

    def country_name(self, obj):
        return ' ,'.join([country.country_name for country in obj.country.all()])


class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User

    def clean(self):
        cleaned_data = self.cleaned_data
        if 'email' in cleaned_data:
            username = cleaned_data.get('email').strip()
            if not len(username):
                raise forms.ValidationError("This email address is required")
            existing_users_with_username = User.objects.filter(username=username)
            if existing_users_with_username.count() > 0 and existing_users_with_username[0] != self.instance:
                raise forms.ValidationError(
                    "This email address is already in use. Please supply a different email address")
            cleaned_data['email'] = username
        return cleaned_data


class NgoUserAdmin(DatawinnerAdmin):
    list_display = ('organization_name', 'country', 'organization_id', 'admin_name', 'admin_email')
    fields = ('email', )
    form = UserAdminForm

    def organization_name(self, obj):
        profile = obj.get_profile()
        return Organization.objects.get(org_id=profile.org_id).name

    def country(self, obj):
        return (Organization.objects.get(org_id=obj.get_profile().org_id)).country_name()

    def organization_id(self, obj):
        return obj.get_profile().org_id

    def admin_name(self, obj):
        return obj.first_name

    def admin_email(self, obj):
        return obj.email

    def queryset(self, request):
        qs = super(NgoUserAdmin, self).queryset(request)
        return qs.filter(groups=Group.objects.filter(name="NGO Admins"))

    def save_model(self, request, obj, form, change):
        username = form.cleaned_data['email']
        obj.username = username
        obj.email = username
        obj.save()


class DWUserChangeForm(UserChangeForm):
    organization_id = CharField(label="Organization ID")

    def __init__(self, *args, **kwargs):
        super(DWUserChangeForm, self).__init__(*args, **kwargs)
        self.fields['organization_id'] = CharField(label="Organization ID")
        if self.instance:
            self.organization_id_field()
            self.fields['password'].widget.attrs['readonly'] = 'readonly'
            self.fields['first_name'].label = "Name"

    class Meta:
        model = User

    def organization_id_field(self):
        org_id = ''
        try:
            user_profile = NGOUserProfile.objects.get(user=self.instance)
            org_id = user_profile.org_id
        except:
            pass
        self.fields['organization_id'] = CharField(label="Organization ID", initial=org_id)


    def clean_organization_id(self):
        org_id = self.cleaned_data.get('organization_id', '')
        try:
            org = Organization.objects.get(org_id__iexact=org_id)
            return org.org_id
        except Organization.DoesNotExist:
            raise ValidationError('Organization with id : %s does not exist.Please enter a valid id' % org_id)


def _remove_default_name_fields():
    user_display_fields =  list(UserAdmin.list_display)
    user_display_fields.remove('first_name')
    user_display_fields.remove('last_name')
    return tuple(user_display_fields)

def export_user_list_to_excel(a,b,c):
    #Custom Method to export user details.
    def is_required(user):
        return True if user.groups.filter(name="NGO Admins").count() or user.groups.filter(name="Project Managers").count() \
            or user.groups.filter(name="Extended Users").count()else False

    def user_role(user):
        if user.groups.filter(name='NGO Admins').count():
            return 'Admin'
        elif user.groups.filter(name='Project Managers').count():
            return 'User'

    list = []
    for ngo_user in NGOUserProfile.objects.all():
        try:
            user = User.objects.get(id=ngo_user.user_id)
            if is_required(user) and not user.is_superuser:
                details = []
                details.append(user.first_name + ' ' + user.last_name)
                details.append(user.username)
                org_id = ngo_user.org_id
                organization = Organization.objects.get(org_id = org_id)
                details.append(organization.name)
                details.append(organization.status)
                details.append(organization.language)
                details.append(user_role(user))
                list.append(details)
        except Exception:
            continue
    headers = ['Name', 'email', 'Organization Name', 'Status', 'Account language','User Role']
    response = export_to_new_excel(headers,list,'user_list')
    return response

class DWUserAdmin(UserAdmin):
    list_filter = ('groups__name',)
    UserAdmin.fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Membership'), {'fields': ('groups', 'organization_id')}),
    )
    readonly_fields = ('last_login', 'date_joined')
    list_display = _remove_default_name_fields() + ('name','organization_name', 'organization_id')
    form = DWUserChangeForm
    actions = [export_user_list_to_excel]

    def name(self,obj):
        return obj.first_name

    def organization_name(self, obj):
        org_id = NGOUserProfile.objects.get(user=obj).org_id
        return Organization.objects.get(org_id=org_id).name


    def organization_id(self, obj):
        return NGOUserProfile.objects.get(user=obj).org_id

    def save_model(self, request, obj, form, change):
        super(DWUserAdmin, self).save_model(request, obj, form, change)

        if change:
            if 'email' in form.changed_data or 'username' in form.changed_data:
                try:
                    existing_digests = PartialDigest.objects.filter(user=obj)
                    if existing_digests:
                        for existing_digest in existing_digests:
                            existing_digest.delete()
                except PartialDigest.DoesNotExist:
                    pass

        if form.cleaned_data.get('organization_id') is not None:
            try:
                user_profile = NGOUserProfile.objects.get(user=obj)
                user_profile.org_id = form.cleaned_data['organization_id']
                user_profile.save()
            except NGOUserProfile.DoesNotExist:
                user_profile = NGOUserProfile()
                user_profile.org_id = form.cleaned_data['organization_id']
                user_profile.title = 'Title'
                user_profile.user = obj
                user_profile.save()


admin.site.unregister(Group)
admin.site.unregister(User)

admin.site.register(OrganizationSetting, OrganizationSettingAdmin)
admin.site.register(OutgoingNumberSetting, admin.ModelAdmin)
admin.site.register(SMSC, admin.ModelAdmin)
admin.site.register(MessageTracker, MessageTrackerAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Network, NetworkAdmin)
admin.site.register(User, DWUserAdmin)
