# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.contrib import admin
from django.contrib.auth.models import User, Group
from registration.models import RegistrationProfile
from datawinners.accountmanagement.models import OrganizationSetting, SMSC, PaymentDetails, MessageTracker, Organization
from mangrove.utils.types import is_empty, is_not_empty

admin.site.disable_action('delete_selected')

class DatawinnerAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

class OrganizationSettingAdmin(DatawinnerAdmin):
    list_display = ('organization_name', 'organization_id', 'type', 'payment_details', 'activation_date')
    fields = ('sms_tel_number', 'smsc')

    def organization_name(self, obj):
        return obj.organization.name

    def organization_id(self, obj):
        return obj.organization.org_id

    def payment_details(self, obj):
        organization = obj.organization
        payment_details = PaymentDetails.objects.filter(organization = organization)
        if not is_empty(payment_details):
            return payment_details[0].preferred_payment

        return "--"

    def type(self, obj):
        return 'Trial' if obj.organization.in_trial_mode else 'Paid'

    def activation_date(self, obj):
        return obj.organization.active_date if obj.organization.active_date is not None else '--'


class MessageTrackerAdmin(DatawinnerAdmin):
    list_display = ("organization_name", "month", "incoming_messages", "outgoing_messages", "total_messages")

    def organization_name(self, obj):
        return obj.organization.name

    def month(self, obj):
        return obj.month

    def incoming_messages(self, obj):
        return obj.incoming_sms_count

    def outgoing_messages(self, obj):
        return obj.outgoing_sms_count

    def total_messages(self, obj):
        return obj.incoming_sms_count + obj.outgoing_sms_count


class OrganizationAdmin(DatawinnerAdmin):
    list_display = ('organization_name', 'complete_address', 'office_phone', 'website', 'paid', 'active_date')

    def organization_name(self, obj):
        return obj.name

    def paid(self, obj):
        return "No" if obj.in_trial_mode else "Yes"

    def complete_address(self, obj):
        complete_address = [obj.address, obj.addressline2, obj.city, obj.zipcode, obj.state, obj.country]
        return ", ".join([element for element in complete_address if is_not_empty(element)])


admin.site.unregister(Group)
admin.site.unregister(User)

admin.site.register(OrganizationSetting, OrganizationSettingAdmin)
admin.site.register(SMSC,DatawinnerAdmin)
admin.site.register(MessageTracker, MessageTrackerAdmin)
admin.site.register(Organization, OrganizationAdmin)