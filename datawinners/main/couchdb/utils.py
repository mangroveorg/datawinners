import requests
from datawinners import settings


def all_db_names(server=settings.COUCH_DB_SERVER):
    all_dbs = requests.get(server + "/_all_dbs", auth=settings.COUCHDBMAIN_CREDENTIALS)
    return filter(lambda x: x.startswith('hni_'), all_dbs.json())


def db_names_with_custom_apps():
    return settings.EXTERNAL_APPS_ORGS
