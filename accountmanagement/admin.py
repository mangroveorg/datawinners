# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.contrib import admin
from django.contrib.auth.models import User, Group
from datawinners.accountmanagement.models import OrganizationSetting

class OrganizationSettingAdmin(admin.ModelAdmin):
    list_display = ('organization_name','organization_id')
    fields = ('sms_tel_number',)

    def organization_name(self,obj):
        return obj.organization.name;

    def organization_id(self,obj):
        return obj.organization.org_id


admin.site.register(OrganizationSetting,OrganizationSettingAdmin)
admin.site.unregister(Group)
admin.site.unregister(User)
