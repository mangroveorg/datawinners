# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf import settings
from mangrove.datastore.database import get_db_manager
from datawinners.main.initial_couch_fixtures import load_all_managers

managers = load_all_managers()

def migrate_01(managers):
    failed_managers = []
    print "Updating existing project that have web device to have smartPhone device"
    for manager in managers:
        print ("Database %s") % (manager.database_name,)
        try:
            projects = manager.load_all_rows_in_view('all_projects')
            for project in projects:
                if 'web' in project['value']['devices'] and 'smartPhone' not in project['value']['devices']:
                    project['value']['devices'] = ["sms", "web", "smartPhone"]

                    print ("Updating project %s devices to have smartPhone option") % (project['value']['name'],)
                    manager.database.save(project)

        except Exception as e:
            failed_managers.append((manager, e.message))

    print 'failed managers if any'
    for manager,exception_message in failed_managers:
        print " %s failed. the reason :  %s" %(manager,exception_message)


migrate_01(managers)
