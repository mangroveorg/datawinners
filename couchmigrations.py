from datawinners import initializer
from main.initial_couch_fixtures import load_all_managers

managers = load_all_managers()

map_fun_submission_docs = """
function(doc){
	if(doc.document_type=='SubmissionLog'){
		emit(doc, null);
	}
}
"""

map_fun_project_docs = """
function(doc){
	if(doc.document_type=='Project'){
		emit(doc, null);
	}
}
"""
map_fun_raw_submission_docs = """
function(doc){
	if(doc.document_type=='RawSubmissionLog'){
		emit(doc, null);
	}
}
"""

map_fun_raw_form_model_docs = """
function(doc){
	if(doc.document_type=='FormModel'){
		emit(doc, null);
	}
}
"""

def migrate_01(managers, map_fun_project_docs, map_fun_raw_form_model_docs, map_fun_submission_docs):
    for manager in managers:
        initializer.run(manager)
        submissions = manager.database.query(map_fun_submission_docs)
        for submission in submissions:
            document = submission.key
            document['event_time'] = document['created']
            if 'voided' in document:
                document.pop('voided')
            manager.database.save(document)

        raw_submissions = manager.database.query(map_fun_raw_submission_docs)
        for submission in raw_submissions:
            manager.database.delete(submission.key)

        projects = manager.database.query(map_fun_project_docs)
        for project in projects:
            document = project.key
            document['language'] = 'en'
            document['data_senders'] = []
            document['reminder_and_deadline'] = {"frequency_enabled": "False", "reminders_enabled": "False"}
            manager.database.save(document)

        form_models = manager.database.query(map_fun_raw_form_model_docs)
        for form_model in form_models:
            document = form_model.key
            if document['form_code'] == 'reg':
                continue
            document['label']['en']= document['label']['eng']
            del document['label']['eng']
            document['metadata']['activeLanguages']= ["en"]
            for index, json_field in enumerate(document['json_fields']):
                json_field['label']['en'] = json_field['label']['eng']
                del json_field['label']['eng']
                json_field['required'] = False
                if json_field['type'] == 'integer':
                    range = json_field['range']
                    del json_field['range']
                    json_field['constraints'] = [['range', range]]
                if json_field['type'] == 'text':
                    length = json_field['length']
                    del json_field['length']
                    json_field['constraints'] = [['length', length]]
                    json_field['required'] = json_field.get('entity_question_flag', False)
                if (json_field['type'] == 'select') | (json_field['type'] == 'select1'):
                    for i, choice in enumerate(json_field['choices']):
                        choice['text']['en'] = choice['text']['eng']
                        del choice['text']['eng']
                        choice['val'] = chr(i + 97)
                        json_field['choices'][i] = choice
                document['json_fields'][index] = json_field

                manager.database.save(document)

migrate_01(managers, map_fun_project_docs, map_fun_raw_form_model_docs, map_fun_submission_docs)
