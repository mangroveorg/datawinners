# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datawinners import settings
from mangrove.form_model.form_model import REPORTER, NAME_FIELD
from mangrove.datastore.entity import get_by_short_code
from mangrove.datastore.database import get_db_manager
from django.contrib.auth.models import User, Group
from datawinners.accountmanagement.models import OrganizationSetting
from datawinners.main.initial_couch_fixtures import load_all_managers
from datetime import datetime
from mangrove.form_model.field import DateField

map_fun_form_model_with_date_field_docs = """
function(doc) {
    if(doc.document_type=='FormModel' && doc.is_registration_model){
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

def migrate_01(managers):
    failed_managers = []
    failed_users = []
    print "Updating existing project that have web device to have smartPhone device"

    for user in User.objects.filter(groups=Group.objects.filter(name='Data Senders')):
        try:
            print 'getting user profile for %s' % user.username
            ngo_user_profile = user.get_profile()
            db = OrganizationSetting.objects.get(organization=ngo_user_profile.org_id).document_store

            print 'getting db manager for %s' % user.username
            manager = get_db_manager(server=settings.COUCH_DB_SERVER, database=db)

            print 'getting reporter entity for %s' % user.username
            reporter_entity = get_by_short_code(manager, ngo_user_profile.reporter_id, [REPORTER])

            print 'setting first name for %s' % user.username
            user.first_name = reporter_entity.value(NAME_FIELD)
            user.save()
        except Exception as e:
            failed_users.append((user.username, e.message))


    for manager in managers:
        print ("Database %s") % (manager.database_name,)
        try:
            rows = manager.load_all_rows_in_view('all_projects')
            for row in rows:
                document = row['value']
                document['devices'] = ["sms", "web", "smartPhone"]

                print ("Updating project %s devices to have smartPhone option") % (document['name'],)
                manager.database.save(document)

        except Exception as e:
            failed_managers.append((manager, e.message))

    for manager in managers:
        try:
            print manager.database
            print manager
            print "migrating date fields"
            form_model_rows = manager.database.query(map_fun_form_model_with_date_field_docs)
            for form_model_row in form_model_rows:
                fields= form_model_row.key['json_fields']
                for field in fields:
                    if field['type'] == 'date':
                        field_name = field['name']
                        date_format = field['date_format']
                        form_code = form_model_row.key['form_code']
                        data_records = manager.database.query(map_fun_data_records_on_a_form_model, key=form_code)
                        for data in data_records :
                            document = data.value
                            value = document['data'][field_name]['value']
                            if not isinstance(value, datetime):
                                document['data'][field_name]['value'] = datetime.strptime(value,
                                    DateField.DATE_DICTIONARY.get(date_format))
                                manager.database.save(document)
        except Exception as e:
            failed_managers.append((manager, e.message))

    print 'failed managers if any'
    for manager,exception_message in failed_managers:
        print " %s failed. the reason :  %s" %(manager, exception_message)

    print 'failed data sender users if any'
    for username,exception_message in failed_users:
        print " %s failed. the reason :  %s" %(username, exception_message)


migrate_01(managers)
