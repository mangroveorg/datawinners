# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datawinners.settings import CRS_ORG_ID
from datawinners.project import models
from django.utils.translation import ugettext_lazy as _
from datawinners.main.database import get_database_manager

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


def link(report_name,language):
    locale = '&__locale=fr_CA' if language == 'fr' else ''
    return '/birt-viewer/frameset?__report=crs/'+ report_name + '.rptdesign' + locale


def get_reports_list(org_id,language):
    if org_id == CRS_ORG_ID:
        return [
                {'link' : link('waybill_sent_and_received', language),'name': _('Way Bill Sent vs Received Report'), 'desc': _('Way bill sent vs received description')},
                {'link' : link('CSR', language),'name': _('CSR'), 'desc': _('Warehouse Commodity Status Report')},
                {'link' : link('LSR', language),'name': _('LSR'), 'desc': _('LSR description')},
                {'link' : link('MSL', language),'name': _('MSL'), 'desc': _('MSL description')},
                {'link' : link('NCSR', language),'name': _('CSR National'), 'desc': _('National Commodity Status Report')},
                {'link' : link('recipient_status_report', language),'name': _('Recipient Status Report'), 'desc': _('Recipient Status Report description')},
                {'link' : link('return_report', language),'name': _('Return Report'), 'desc': _('Return Report description')},
                {'link' : link('billOfLadingVsWayBillPort', language),'name': _('Bill Of Lading vs Way Bill Port'), 'desc': _('Bill Of Lading vs Way Bill Port description')},
        ]
    return  []