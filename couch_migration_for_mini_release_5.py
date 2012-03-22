# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from mangrove.form_model.form_model import get_form_model_by_code
from datawinners.main.initial_couch_fixtures import load_all_managers
from mangrove.contrib.deletion import create_default_delete_form_model, ENTITY_DELETION_FORM_CODE
from mangrove.bootstrap.initializer import sync_views

managers = load_all_managers()

def migrate_01(managers):
    failed_managers = []
    for manager in managers:
        try:
            print manager.database
            print manager
            print "Syncing views"
            sync_views(manager)
            print "making the delete form model"
            try:
                form_model = get_form_model_by_code(manager, ENTITY_DELETION_FORM_CODE)
                form_model.delete()
            except Exception:
                pass
            finally:
                create_default_delete_form_model(manager)
        except Exception as e:
            failed_managers.append((manager,e.message))

    print 'failed managers if any'
    for manager,exception_mesage in failed_managers:
        print " %s failed. the reason :  %s" %(manager,exception_mesage)


migrate_01(managers)

