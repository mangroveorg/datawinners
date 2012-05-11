# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datawinners.settings import CRS_ORG_ID
from datawinners.main.utils import get_database_manager
from datawinners.project import models
from django.utils.translation import ugettext_lazy as _

def get_all_project_for_user(user):
    if user.get_profile().reporter:
        return models.get_all_projects(get_database_manager(user), user.get_profile().reporter_id)
    return models.get_all_projects(get_database_manager(user))


def get_visibility_settings_for(user):
    if user.get_profile().reporter:
        return "disable_link_for_reporter", "none"
    return "",""

def get_page_heading(user):
    if user.get_profile().reporter:
        return "Data Submission"
    return "All Data"


def link(report_name):
    return '/birt-viewer/frameset?__report=crs/'+ report_name + '.rptdesign'


def get_reports_list(org_id):
    if org_id == CRS_ORG_ID:
        return [
                {'link' : link('waybill_sent_and_received'),'name': _('Way Bill Sent vs Received Report'), 'desc': _('Way bill sent vs received description')},
                {'link' : link('CSR'),'name': _('CSR'), 'desc': _('CSR description')},
                {'link' : link('LSR'),'name': _('LSR'), 'desc': _('LSR description')},
                {'link' : link('MSL'),'name': _('MSL'), 'desc': _('MSL description')},
                {'link' : link('csr_warehouse'),'name': _('CSR Warehouse'), 'desc': _('CSR Warehouse description')},
                {'link' : link('recipient_status_report'),'name': _('Recipient Status Report'), 'desc': _('Recipient Status Report description')},
                {'link' : link('return_report'),'name': _('Return Report'), 'desc': _('Return Report description')},
                {'link' : link('billOfLadingVsWayBillPort'),'name': _('Bill Of Lading vs Way Bill Port'), 'desc': _('Bill Of Lading vs Way Bill Port description')},
        ]
    return  []