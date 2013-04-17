from datawinners.main.initial_couch_fixtures import load_all_managers
from datawinners.main.utils import sync_views
from mangrove.contrib.deletion import ENTITY_DELETION_FORM_CODE
from mangrove.form_model.form_model import get_form_model_by_code

managers = load_all_managers()

def migrate_story_1924(managers):
    failed_managers = []
    for manager in managers:
        try:
            print manager.database
            print manager
            print "Syncing views"
            sync_views(manager)
            print "start: removing maxlength constraint from DeletionFormModel"
            try:
                form_model = get_form_model_by_code(manager, ENTITY_DELETION_FORM_CODE)

                for field in form_model.fields:
                    if field.code == 's':
                        field.set_constraints([])
                form_model.save()
                print "end: removing maxlength constraint from DeletionFormModel"
            except Exception as e:
                print "error:" + e.message
        except Exception as e:
            failed_managers.append((manager, e.message))

    print 'failed managers if any'
    for manager, exception_message in failed_managers:
        print " %s failed. the reason :  %s" % (manager, exception_message)

migrate_story_1924(managers)


