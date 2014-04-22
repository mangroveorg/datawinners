import logging
import re
from mangrove.datastore.documents import FormModelDocument
from mangrove.form_model.form_model import FormModel
from datawinners.main.couchdb.utils import all_db_names
from datawinners.main.database import get_db_manager
from migration.couch.utils import migrate, mark_as_completed
from mangrove.transport.contract.survey_response import convert_dict_keys_to_lowercase
from mangrove.transport.repository.survey_responses import survey_responses_by_form_code


def convert_field_code_to_lower_case(db_name):
    logger = logging.getLogger(db_name)
    try:
        dbm = get_db_manager(db_name)
        rows = dbm.load_all_rows_in_view('questionnaire', reduce=False)
        for row in rows:
            form_model = FormModel.new_from_doc(dbm, FormModelDocument.wrap(row['value']))
            is_upper = False
            for field in form_model.fields:
                if re.match(r".*[A-Z]+.*", field.code):
                    logger.info("doc id: %s, field code: %s", form_model.id, field.code)
                    is_upper = True
                    field._dict['code'] = field.code.lower()
            if is_upper:
                form_model.save()
                survey_responses = survey_responses_by_form_code(dbm, form_model.form_code)
                for survey_response in survey_responses:
                    convert_dict_keys_to_lowercase(survey_response.values)
                    survey_response.save()
                    logger.info("Modified survey response id: %s" % survey_response.uuid)

        mark_as_completed(db_name)
    except Exception as e:
        logger.exception(e.message)


migrate(all_db_names(), convert_field_code_to_lower_case, version=(11, 0, 5), threads=3)
