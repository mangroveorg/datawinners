from django.contrib import admin
from datawinners.smstester.models import OutgoingMessage


class OutgoingMessageAdmin(admin.ModelAdmin):
    list_display = ['from_msisdn', 'to_msisdn', 'message', 'sent_date']
    actions = ['delete_selected']

admin.site.register(OutgoingMessage, OutgoingMessageAdmin)
