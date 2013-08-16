from django.contrib.auth.models import User
from datawinners.accountmanagement.models import OrganizationSetting
from datawinners.main.utils import get_database_name
from mangrove.datastore.database import get_db_manager as mangrove_db_manager
from datawinners import settings

TEST_EMAILS = ['tester150411@gmail.com', 'chinatwu2@gmail.com', 'chinatwu3@gmail.com', 'gerard@mailinator.com',
               'samuel@mailinator.com', 'mamytest@mailinator.com']


def test_document_stores():
    document_stores = []
    for email in TEST_EMAILS:
        document_stores.append(get_database_name(User.objects.get(username=email)))
    return document_stores


def document_stores():
    return [org.document_store for org in OrganizationSetting.objects.all()]


def get_db_manager(database_name):
    return mangrove_db_manager(server=settings.COUCH_DB_SERVER, database=database_name,
                               credentials=settings.COUCHDBMAIN_CREDENTIALS)


def get_database_manager(user):
    return get_db_manager(get_database_name(user))