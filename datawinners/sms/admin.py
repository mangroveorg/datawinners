from django.contrib import admin
from datawinners.sms.models import SMS



class SMSAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'organization', 'status','delivered_at', 'message', 'msg_from', 'msg_to', 'msg_type', 'smsc')
    list_filter = ['delivered_at', "status","smsc", "msg_type"]
    search_fields = ['msg_to']
admin.site.register(SMS,SMSAdmin)
