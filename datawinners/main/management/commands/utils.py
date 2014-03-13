from django.contrib.auth.models import User
from datawinners.accountmanagement.models import OrganizationSetting
from datawinners.main.utils import get_database_name

TEST_EMAILS = ['chinatwu2@gmail.com', 'chinatwu3@gmail.com', 'gerard@mailinator.com',
               'samuel@mailinator.com', 'mamytest@mailinator.com', 'quotareached@mailinator.com']

def test_document_stores():
    document_stores = []
    for email in TEST_EMAILS:
        document_stores.append(get_database_name(User.objects.get(username=email)))
    return document_stores


def document_stores():
    return [org.document_store for org in OrganizationSetting.objects.all()]


def document_stores_to_process(args):
    if "syncall" in args:
        return document_stores()

    return test_document_stores()
