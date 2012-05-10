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

def get_reports_list(org_id):
    if org_id == CRS_ORG_ID:
        return [{'link' : '/birt-viewer/frameset?__report=crs/waybill_sent_and_received.rptdesign','name': 'WayBillSentVSReceived', 'desc': 'Way bill sent vs received'}]
    return  []