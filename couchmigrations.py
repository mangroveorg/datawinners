from datawinners.main.initial_couch_fixtures import load_all_managers

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
	if(doc.document_type=='SubmissionLog'){
		emit(doc, null);
	}
}
"""

for manager in managers:
    submissions = manager.database.query(map_fun_submission_docs)
    for submission in submissions:
        document = submission.key
        document['event_time'] = document['created']
        if 'voided' in document:
            document.pop('voided')
        manager.database.save(document)

    raw_submissions = manager.database.query(map_fun_submission_docs)
    for submission in raw_submissions:
        manager.database.delete(submission.key)

    projects = manager.database.query(map_fun_project_docs)
    for project in projects:
        project['language'] = 'en'
        project['datasenders'] = []
        project['reminder_and_deadline'] = {"frequency_enabled": "False","reminders_enabled": "False"}
        manager.database.save(project)

