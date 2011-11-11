# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.contrib import admin
from django.contrib.auth.models import User, Group
from datawinners.accountmanagement.models import OrganizationSetting, SMSC, PaymentDetails, MessageTracker
from mangrove.utils.types import is_empty

class OrganizationSettingAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'organization_id', 'payment_details')
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

admin.site.register(OrganizationSetting, OrganizationSettingAdmin)
admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(SMSC)
admin.site.register(MessageTracker, MessageTrackerAdmin)