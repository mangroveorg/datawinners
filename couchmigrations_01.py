from datawinners import initializer
from main.initial_couch_fixtures import load_all_managers

managers = load_all_managers()

map_fun_project_docs = """
function(doc){
	if(doc.document_type=='Project'){
		emit(doc, null);
	}
}
"""

def migrate_01(managers, map_fun_project_docs):
    for manager in managers:
        projects = manager.database.query(map_fun_project_docs)
        for project in projects:
            print project
            document = project.key
            document['reminder_and_deadline'] = {"deadline_type": "Following",
                                      "should_send_reminder_to_all_ds": False,
                                      "has_deadline": True,
                                      "deadline_month": "5",
                                      "frequency_period": "month"}

            manager.database.save(document)

def migrate():
    migrate_01(managers, map_fun_project_docs)
    print "Done"


migrate()
