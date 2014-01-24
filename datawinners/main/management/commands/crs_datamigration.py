# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from collections import OrderedDict
from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.datastore.database import get_db_manager
from django.core.management.base import BaseCommand
from mangrove.transport.contract.submission import Submission
from datawinners import settings
from datawinners.accountmanagement.models import Organization, OrganizationSetting
from datawinners.custom_reports.crs.handler import CRSCustomReportHandler
from south.db import db

class Command(BaseCommand):
    def handle(self, *args, **options):
        crs_org = Organization.objects.get(org_id =settings.CRS_ORG_ID)
        document_store = OrganizationSetting.objects.get(organization = crs_org).document_store
        crs_database_manager = get_db_manager(server=settings.COUCH_DB_SERVER, database=document_store)

        crs_questionnaires = [settings.WAYBILL_SENT_QUESTIONNAIRE_CODE, settings.WAYBILL_SENT_BY_SITE,
                              settings.WAYBILL_RECEIVED_BY_SITE, settings.SFE_DISTRIBUTION_CODE,
                              settings.SFM_DISTRIBUTION_CODE, settings.WAYBILL_RECEIVED_BY_WH,
                              settings.WAYBILL_RECEIVED_QUESTIONNAIRE_CODE, settings.PACKING_LIST_QUESTIONNAIRE_CODE,
                              settings.BREAK_BULK_RECEIVED_PORT_QUESTIONNAIRE_CODE,
                              settings.BILL_OF_LADING_QUESTIONNAIRE_CODE, settings.PHYSICAL_INVENTORY_QUESTIONNAIRE_CODE,
                              settings.FFA_DISTRIBUTION_CODE, settings.BAV_CPS_CODE, settings.BAV_SF_CODE,
                              settings.BAV_FFA_CODE, settings.CONTAINER_RECEIVED_PORT_QUESTIONNAIRE_CODE,
                              settings.CONTAINER_SENT_QUESTIONNAIRE_CODE, settings.CPS_DISTRIBUTION_CODE,
                              settings.NO_OF_RECIPIENT_CPS_CODE, settings.NO_OF_RECIPIENT_FFA_CODE,
                              settings.NO_OF_RECIPIENT_SFE_CODE, settings.NO_OF_RECIPIENT_SFM_CODE,
                              settings.BREAK_BULK_SENT_QUESTIONNAIRE_CODE ]
        try:
           form_code = list(args)[0]
           if form_code in crs_questionnaires:
               crs_questionnaires = [form_code]
        except Exception:
            pass

        try:
            datarecords_id = list(args)[1:]
            if not len(datarecords_id):
                datarecords_id = None
        except KeyError:
            datarecords_id = None

        handler = CRSCustomReportHandler()
        for questionnaire_code in crs_questionnaires:
            print 'getting the questionnaire'
            questionnaire= get_form_model_by_code(crs_database_manager, questionnaire_code)
            print 'migrations for %s' % questionnaire_code
            submissions = self._load_submissions_for(questionnaire_code, crs_database_manager,
                datarecords_id=datarecords_id)
            print 'adding to sql'
            for submission in submissions:
                data_record = submission.data_record
                formatted_submission = self._get_formatted_submission(data_record, questionnaire)
                try:
                    db.start_transaction()
                    handler.handle(questionnaire_code,
                        formatted_submission,
                        data_record.id)
                    db.commit_transaction()
                except Exception as e:
                    db.rollback_transaction()
                    print formatted_submission
                    print data_record.id
                    print e.message
            print 'finished adding to sql for questionnaire %s' % questionnaire_code

    def _load_submissions_for(self, questionnaire_code, crs_database_manager, datarecords_id=None):
        startkey = [questionnaire_code]
        endkey = [questionnaire_code, {}]
        print 'loading submissions for %s' % questionnaire_code
        rows = crs_database_manager.view.submissionlog(reduce=False, startkey=startkey, endkey=endkey)
        return [Submission.new_from_doc(dbm=crs_database_manager,
            doc = Submission.__document_class__.wrap(row['value']))
            for row in rows if row['value']['status'] == True and
            (datarecords_id is None or row["value"]["data_record_id"] in datarecords_id)]

    def _get_value_from_data_record(self, data_record, question):
        for key in data_record.data.keys():
            if key.strip() == unicode(question.name).strip():
                return data_record.data[key]['value']
        return None

    def _get_formatted_submission(self, data_record, questionnaire):
        questions = questionnaire.fields
        formatted_data = OrderedDict()
        for question in questions:
            formatted_data[question.code] = self._get_value_from_data_record(data_record, question)
        return formatted_data
