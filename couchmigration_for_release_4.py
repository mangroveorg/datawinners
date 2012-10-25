# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from mangrove.datastore.entity_type import get_all_entity_types
from django.utils import translation
from datawinners import initializer
from datawinners.main.initial_couch_fixtures import load_all_managers
from datawinners.entity.helper import create_registration_form

managers = load_all_managers()

map_fun_raw_form_model_docs = """
function(doc){
	if(doc.document_type=='FormModel'){
		emit(doc, null);
	}
}
"""

def migrate_01(managers, map_fun_raw_form_model_docs):
    failed_managers = []
    for manager in managers:
        try:
            print manager.database
            print manager
            print 'running initializer'
            initializer.run(manager)
            print 'syncing form models'
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
                        json_field['label'] = json_field['name']
                        document['json_fields'][index] = json_field
                    document["validators"] = [{"cls": "mandatory"}]
                manager.database.save(document)
            print 'syncing entity reg forms'
            entity_types = get_all_entity_types(manager)
            # django.core.management.base forces the locale to en-us.
            translation.activate('en')
            for entity_type in entity_types:
                if entity_type != ['reporter']:
                    create_registration_form(manager, entity_type)
            print "done for %s"%(manager,)
        except Exception as e:
            failed_managers.append((manager,e.message))


    print 'failed managers if any'
    for manager,exception_mesage in failed_managers:
        print " %s failed. the reason :  %s" %(manager,exception_mesage)

migrate_01(managers, map_fun_raw_form_model_docs)

