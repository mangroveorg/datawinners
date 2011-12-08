# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.contrib import admin
from django.contrib.auth.models import User, Group
from datawinners.accountmanagement.models import SMSC, PaymentDetails, MessageTracker, OrgSettings
from mangrove.utils.types import is_empty

#class OrgSettingAdmin(admin.ModelAdmin):
#    list_display = ('organization_name', 'organization_id', 'type', 'payment_details', 'activation_date')
#    fields = ('sms_tel_number', 'smsc')
#
#    def has_delete_permission(self, request, obj=None):
#        return False
#
#    def organization_name(self, obj):
#        return obj.organization.name
#
#    def organization_id(self, obj):
#        return obj.organization.org_id
#
#    def payment_details(self, obj):
#        organization = obj.organization
#        payment_details = PaymentDetails.objects.filter(organization = organization)
#        if not is_empty(payment_details):
#            return payment_details[0].preferred_payment
#
#        return "--"
#
#    def type(self, obj):
#        return 'Trial' if obj.organization.in_trial_mode else 'Paid'
#
#    def activation_date(self, obj):
#        return obj.organization.active_date if obj.organization.active_date is not None else '--'


class MessageTrackerAdmin(admin.ModelAdmin):
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

admin.site.register(OrgSettings, OrganizationSettingAdmin)
admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(SMSC)
admin.site.register(MessageTracker, MessageTrackerAdmin)