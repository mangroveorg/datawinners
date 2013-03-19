# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datetime import datetime
from mangrove.datastore.entity import _get_all_entities_of_type
from mangrove.form_model.field import DateField
from datawinners.main.initial_couch_fixtures import load_all_managers

map_fun_form_model_with_date_field_docs = """
function(doc) {
    if(doc.document_type=='FormModel'){
        for (field in doc.json_fields) {
            if (doc.json_fields[field].type == 'date') {
                emit(doc, null);
		break;
            }
        }
    }
}"""

map_fun_data_records_on_a_form_model = """
function (doc) {
    if (doc.document_type == 'DataRecord') {
        emit(doc.submission['form_code'], doc);
    }
}"""

managers = load_all_managers()

def migrate_01(managers, map_fun_form_model_with_date_field_docs):
    failed_managers = []
    for manager in managers:
        try:
            print manager.database
            print manager
            print "migrating date fields"
            try:
                form_model_rows = manager.database.query(map_fun_form_model_with_date_field_docs)
                for form_model_row in form_model_rows:
                    fields= form_model_row.key['json_fields']
                    for field in fields:
                        if field['type'] == 'date':
                            field_name = field['name']
                            date_format = field['date_format']
                            if form_model_row.key['is_registration_model']:
                                entities = _get_all_entities_of_type(manager, form_model_row.key['entity_type'])
                                for entity in entities :
                                    value = entity.value(field_name)
                                    if not isinstance(value, datetime):
                                        entity.data[field_name]['value'] = datetime.strptime(value, DateField.DATE_DICTIONARY.get(date_format))
                                        entity.save()
                            else :
                                form_code = form_model_row.key['form_code']
                                data_records = manager.database.query(map_fun_data_records_on_a_form_model, key=form_code)
                                for data in data_records :
                                    document = data.value
                                    value = document['data'][field_name]['value']
                                    if not isinstance(value, datetime):
                                        document['data'][field_name]['value'] = datetime.strptime(value, DateField.DATE_DICTIONARY.get(date_format))
                                        manager.database.save(document)
            except Exception as e:
                print e.message
        except Exception as e:
            failed_managers.append((manager, e.message))

    print 'failed managers if any'
    for manager, exception_message in failed_managers:
        print " %s failed. the reason :  %s" % (manager, exception_message)


migrate_01(managers, map_fun_form_model_with_date_field_docs)

