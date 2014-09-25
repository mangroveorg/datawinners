from datetime import datetime

from django.contrib import admin
from mangrove.form_model.field import ExcelDate

from datawinners.project.submission.export import create_excel_response
from datawinners.sms.models import SMS


def export_sms_details_to_excel(modeladmin, request, query_set):
    list = []
    for sms in query_set:
        delivered_date_time = ExcelDate(datetime.combine(sms.delivered_at, datetime.min.time()),
                                        'dd.mm.yyyy') if sms.delivered_at else None
        list.append([sms.organization_id, sms.status, delivered_date_time, sms.msg_from, sms.msg_to, sms.message])

    headers = ['Organisation Id', 'Status', 'Delivery Date', 'Message from Number', 'Message to Number', 'Content']
    response = create_excel_response(headers, list, 'sms_list')
    return response


class SMSAdmin(admin.ModelAdmin):
    list_display = (
    'message_id', 'organization', 'status', 'delivered_at', 'message', 'msg_from', 'msg_to', 'msg_type', 'smsc')
    list_filter = ['delivered_at', "status", "smsc", "msg_type"]
    search_fields = ['msg_to', 'organization__org_id']
    actions = [export_sms_details_to_excel]

    class Media:
        js = ("/admin/jsi18n",)


admin.site.register(SMS, SMSAdmin)
