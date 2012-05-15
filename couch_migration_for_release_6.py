# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datawinners.main.initial_couch_fixtures import load_all_managers

managers = load_all_managers()

def migrate_01(managers):
    failed_managers = []
    print "Updating existing project that have web device to have smartPhone device"
    for manager in managers:
        print ("Database %s") % (manager.database_name,)
        try:
            rows = manager.load_all_rows_in_view('all_projects')
            for row in rows:
                document = row['value']
                if 'smartPhone' not in document['devices']:
                    document['devices'] = ["sms", "web", "smartPhone"]

                    print ("Updating project %s devices to have smartPhone option") % (document['name'],)
                    manager.database.save(document)

        except Exception as e:
            failed_managers.append((manager, e.message))

    print 'failed managers if any'
    for manager,exception_message in failed_managers:
        print " %s failed. the reason :  %s" %(manager, exception_message)


migrate_01(managers)
