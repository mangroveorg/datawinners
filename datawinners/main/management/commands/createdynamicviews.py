import logging

from django.core.management.base import BaseCommand
from mangrove.datastore.report_config import get_report_config

from datawinners.main.database import  get_db_manager
from datawinners.main.management.commands.utils import document_stores_to_process
from datawinners.report.admin import get_report_view_name, _get_map_function, _combined_view_key, \
    _form_key_for_couch_view
from datawinners.report.helper import strip_alias, distinct, get_indexable_question

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        print "Creating Dynamic Views for Reports within DW"
        for database_name in document_stores_to_process(args):
            dbm = get_db_manager(database_name)
            report_configs = dbm.database.view("all_report_configs/all_report_configs")
            for report_config in report_configs:
                report_id = report_config.id
                report_config_doc = report_config.value
                config = get_report_config(dbm, report_id)
                if not report_config_doc.get('type', None):
                    print ("Database %s") % database_name
                    print "Create Dynamic Views for %s" % report_config_doc.get('name', "")
                    filter_fields = [f['field'] for f in config.filters]
                    date_field = config.date_filter and [strip_alias(config.date_filter['field'])] or []
                    indexes = distinct([strip_alias(get_indexable_question(qn)) for qn in filter_fields])
                    questionnaire_ids = '"{0}"'.format('", "'.join([questionnaire['id'] for questionnaire in config.questionnaires]))
                    dbm.create_view(get_report_view_name(report_id, "_".join(indexes + date_field)), _get_map_function(questionnaire_ids, _combined_view_key(map(_form_key_for_couch_view, indexes + date_field))), "_count")
                    date_field and dbm.create_view(get_report_view_name(report_id, date_field[0]), _get_map_function(questionnaire_ids, _form_key_for_couch_view(date_field[0])), "_count")
        print "Done."
