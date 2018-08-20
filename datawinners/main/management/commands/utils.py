from django.contrib.auth.models import User
from datawinners.accountmanagement.models import OrganizationSetting
from datawinners.main.utils import get_database_name

TEST_EMAILS = ['chinatwu2@gmail.com', 'chinatwu3@gmail.com', 'gerard@mailinator.com',
               'samuel@mailinator.com', 'mamytest@mailinator.com', 'quotareached@mailinator.com']

def test_document_stores():
    document_stores = ["public"]
    for email in TEST_EMAILS:
        document_stores.append(get_database_name(User.objects.get(username=email)))
    return document_stores


def document_stores():
    doc_stores = [org.document_store for org in OrganizationSetting.objects.all()]
    doc_stores.append("public")
    return doc_stores


def document_stores_to_process(args):
    if "syncall" in args:
        return document_stores()

    if len(args) == 1 and args[0].startswith("hni_"):
        return [args[0]]

    return test_document_stores()
