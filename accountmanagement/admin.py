# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.contrib import admin
from django.contrib.auth.models import User, Group
from datawinners.accountmanagement.models import OrganizationSetting, SMSC

class OrganizationSettingAdmin(admin.ModelAdmin):
    list_display = ('organization_name', 'organization_id', 'inbound_sms', 'outbound_sms', 'total_sms')
    fields = ('sms_tel_number', 'smsc')

    def organization_name(self, obj):
        return obj.organization.name

    def organization_id(self, obj):
        return obj.organization.org_id

    def inbound_sms(self, obj):
        return obj.incoming_sms_count

    def outbound_sms(self, obj):
        return obj.outgoing_sms_count

    def total_sms(self, obj):
        return obj.incoming_sms_count + obj.outgoing_sms_count


admin.site.register(OrganizationSetting, OrganizationSettingAdmin)
admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(SMSC)
