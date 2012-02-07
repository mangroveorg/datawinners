# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datawinners import initializer
from datawinners.main.initial_couch_fixtures import load_all_managers

managers = load_all_managers()

map_fun_raw_form_model_docs = """
function(doc){
	if(doc.document_type=='FormModel'){
		emit(doc, null);
	}
}
"""

def migrate_01(managers, map_fun_raw_form_model_docs):
    for manager in managers:
        initializer.run(manager)

        form_models = manager.database.query(map_fun_raw_form_model_docs)
        for form_model in form_models:
            document = form_model.key
            language = document['metadata']['activeLanguages'][0]
            if document['form_code'] == 'reg':
                document['metadata']['activeLanguages'] = ["en"]
                document['is_registration_model'] = True
                document["validators"] = [
                        {"cls": "mandatory"},
                        {"cls": "mobile_number_mandatory_for_reporter"},
                        {"cls": "at_least_one_location_field_must_be_answered_validator"}
                ]
            else:
                document['is_registration_model'] = False
                for index, json_field in enumerate(document['json_fields']):
                    json_field['label'][language] = json_field['name']
                    document['json_fields'][index] = json_field
                document["validators"] = [{"cls": "mandatory"}]
            manager.database.save(document)

migrate_01(managers, map_fun_raw_form_model_docs)
