import logging
import datetime
from mangrove.datastore.database import DatabaseManager, get_db_manager, remove_db_manager
from mangrove.form_model.form_model import FormModel
from mangrove.datastore.documents import FormModelDocument
from find_all_db_managers import all_db_names
import settings

logger = logging.getLogger("django")
db_server = "http://localhost:5984"
db_credentials = settings.COUCHDBMAIN_CREDENTIALS

def delete_label_language_setting_on_form_model(form_model_row_value, active_language):
    label_dict = form_model_row_value["label"]
    if label_dict is None:
        return form_model_row_value
    form_model_row_value["label"] = label_dict.get(active_language, None) or label_dict.values()[0]

    return form_model_row_value

def delete_label_language_setting_on_field(form_model_row_value, active_language):
    fields = form_model_row_value['json_fields']
    for field in fields:
        field['label'] = field['label'].get(active_language, None) or field['label'].values()[0]
        if field.has_key('language'):
            del field['language']

    return form_model_row_value


def delete_text_language_setting_on_field_choices(form_model_row_value, active_language):
    fields = form_model_row_value['json_fields']
    for field in fields:
        if field.has_key('choices'):
            choices = field['choices']
            for option in choices:
                option['text'] = option['text'].get(active_language, None) or option['text'].values()[0]

    return form_model_row_value


def delete_language_redundant_settings(form_model_row_value):
    active_language = form_model_row_value["metadata"]["activeLanguages"]

    if isinstance(active_language, list):
        active_language = active_language[0]

    delete_label_language_setting_on_form_model(form_model_row_value, active_language)
    delete_label_language_setting_on_field(form_model_row_value, active_language)
    delete_text_language_setting_on_field_choices(form_model_row_value, active_language)

    return form_model_row_value

def delete_language_setting_for_form_models(dbm):
    assert isinstance(dbm, DatabaseManager)
    rows = dbm.load_all_rows_in_view('questionnaire')

    for row in rows:
        try:
            form_model_row_value = row['value']
            form_model_row_value = delete_language_redundant_settings(form_model_row_value)
            doc = FormModelDocument.wrap(form_model_row_value)
            form_model = FormModel.new_from_doc(dbm, doc)
            form_model.save()
        except Exception as e:
            print ("*******************form model error *************************************", row['key'])
            print e
            print "*************************************************"

def delete_redundant_language_setting_from_form():
    dbs = all_db_names(db_server)

    for db_name in dbs:
        try:
            logger.info(db_name)
            print db_name
            manager = get_db_manager(server=db_server, database=db_name,credentials=db_credentials)
            delete_language_setting_for_form_models(manager)
            remove_db_manager(manager)
        except Exception as e:
            print ("******************************************", db_name)
            print e
            print ("***************************************************")

if __name__ == "__main__":
    starttime = datetime.datetime.now()
    delete_redundant_language_setting_from_form()
    endtime = datetime.datetime.now()
    interval=(endtime - starttime).seconds

    print 'Total time: %d' % interval