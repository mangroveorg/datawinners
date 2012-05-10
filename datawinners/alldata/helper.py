# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datawinners.local_settings import CRS_ORG_ID
from datawinners.main.utils import get_database_manager
from datawinners.project import models

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
                {'link' : link('waybill_sent_and_received'),'name': 'Way Bill Sent vs Received', 'desc': 'Way bill sent vs received'},
                {'link' : link('CSR'),'name': 'CSR', 'desc': 'CSR'},
                {'link' : link('LSR'),'name': 'LSR', 'desc': 'LSR'},
                {'link' : link('MSL'),'name': 'MSL', 'desc': 'MSL'},
                {'link' : link('recipient_status_report'),'name': 'Recipient Status Report', 'desc': 'Recipient Status Report'},
                {'link' : link('return_report'),'name': 'Return Report', 'desc': 'Return Report'},
                {'link' : link('theoretical_vs_physical_inventory'),'name': 'Theoretical vs Physical Inventory Report', 'desc': 'Theoretical vs Physical Inventory Report'},
                {'link' : link('billOfLadingVsWayBillPort'),'name': 'Bill Of Lading vs Way Bill Port', 'desc': 'Bill Of Lading vs Way Bill Port'},
        ]
    return  []