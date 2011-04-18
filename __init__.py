# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'datawinners.settings'

from datawinners.reports.initial_couch_fixtures import load_data
from mangrove.datastore.database import _delete_db_and_remove_db_manager,get_db_manager

_delete_db_and_remove_db_manager(get_db_manager())
load_data()