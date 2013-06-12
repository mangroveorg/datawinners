from django.contrib.auth.models import User
from accountmanagement.models import OrganizationSetting
from main.utils import get_database_name

def test_document_stores():
    document_stores = []
    test_emails = ['tester150411@gmail.com', 'chinatwu2@gmail.com', 'chinatwu3@gmail.com', 'gerard@mailinator.com']
    for email in test_emails:
        document_stores.append(get_database_name(User.objects.get(username=email)))
    return document_stores


def document_stores():
    return [org.document_store for org in OrganizationSetting.objects.all()]
