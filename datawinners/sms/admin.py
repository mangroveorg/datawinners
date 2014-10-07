from datetime import datetime

from django.contrib import admin
from django.db.models import Q

from mangrove.form_model.field import ExcelDate
from datawinners.project.submission.export import create_excel_response
from datawinners.sms.models import SMS
from datawinners.common.admin.utils import get_text_search_filter, get_admin_panel_filter


class SMSAdmin(admin.ModelAdmin):
    list_display = (
    'message_id', 'organization', 'status', 'delivered_at', 'message', 'msg_from', 'msg_to', 'msg_type', 'smsc')
    list_filter = ['delivered_at', "status", "smsc", "msg_type"]
    search_fields = ['msg_to', 'organization__org_id']

    def export_sms_details_to_excel(modeladmin, request, query_set):
        list = []

        textSearchFilter = get_text_search_filter(request.GET, SMSAdmin.search_fields)
        adminPanelFilter = get_admin_panel_filter(request.GET)

        filteredSms = SMS.objects.all().filter(Q(**adminPanelFilter) & (textSearchFilter))
        for sms in filteredSms:
            delivered_date_time = ExcelDate(datetime.combine(sms.delivered_at, datetime.min.time()),
                                            'dd.mm.yyyy') if sms.delivered_at else None
            list.append([sms.organization_id, sms.status, delivered_date_time, sms.msg_from, sms.msg_to, sms.msg_type, sms.message])

        headers = ['Organisation Id', 'Status', 'Delivery Date', 'Message from Number', 'Message to Number', 'Message Type', 'Content']
        response = create_excel_response(headers, list, 'sms_list')
        return response

    actions = [export_sms_details_to_excel]

    class Media:
        js = ("/admin/jsi18n",)



admin.site.register(SMS, SMSAdmin)
