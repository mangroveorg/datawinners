# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import datetime
from datawinners.accountmanagement.models import NGOUserProfile, OrganizationSetting, Organization

try:
    from resources.local_settings import DATABASES
except Exception as e:
    print "local_settings file is not available"

def get_connection_args():
    db = DATABASES['default']
    args = dict(database = db['NAME'],
                user = db['USER'])

    for arg in ['HOST', 'PORT', 'PASSWORD']:
        value = db.get(arg)
        if value:
            args[arg.lower()] = value
    return args

class DatabaseManager(object):
    def get_activation_code(self, email):
        """
        Function to get activation code for the given email id from SQLite3 database

        Args:
        'email' is the email address of the organization
        'database_name' is the relative path of the database from mangrove/func_tests/framework/utils.
        This is optional field and default value is '../../../src/datawinners/mangrovedb'

        Return activation code
        """
        from registration.models import RegistrationProfile

        return RegistrationProfile.objects.get(user__email=email).activation_key

    def set_sms_telephone_number(self, telephone_number, email):
        """
        Function to set the SMS telephone number for the organization

        Args:
        'telephone_number' is the unique telephone number for the organization on which organization will do submission
        'email' is the email address of the organization
        'database_name' is the relative path of the database from mangrove/func_tests/framework/utils.
        This is optional field and default value is '../../../src/datawinners/mangrovedb'
        """
        ngo_user_profile = NGOUserProfile.objects.get(user__email=email)
        org_setting = OrganizationSetting.objects.get(organization__org_id=ngo_user_profile.org_id)

        org_setting.sms_tel_number = telephone_number
        org_setting.save()

    def delete_organization_all_details(self, email):
        """
        Function to delete all the organization related details

        Args:
        'email' is the email address of the organization
        'database_name' is the relative path of the database from mangrove/func_tests/framework/utils.
        This is optional field and default value is '../../../src/datawinners/mangrovedb'
        """
        from django.contrib.auth.models import User
        user = User.objects.get(email = email)
        ngo_user_profile = NGOUserProfile.objects.get(user=user)
        org = Organization.objects.get(org_id = ngo_user_profile.org_id)
        org_setting = OrganizationSetting.objects.get(organization=org)

        document_store = org_setting.document_store

        org.delete()
        user.delete()

        return document_store

    def update_active_date_to_expired(self, email, date):
        org = self.get_organization_by_email(email)

        active_date = datetime.datetime.today().replace(microsecond=0) - datetime.timedelta(date)
        org.active_date = active_date
        org.save()

    def get_organization_by_email(self, email):
        ngo_user_profile = NGOUserProfile.objects.get(user__email=email)
        return Organization.objects.get(org_id = ngo_user_profile.org_id)

        

if __name__ == "__main__":
    db = DatabaseManager()
    dbname = db.delete_organization_all_details("ngo993cmv@ngo.com")
    print dbname
