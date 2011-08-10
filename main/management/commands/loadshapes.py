from django.core.management.base import BaseCommand
import os
from datawinners import settings, initializer
from datawinners.accountmanagement.models import OrganizationSetting
from datawinners.main.initial_couch_fixtures import load_manager_for_default_test_account, load_all_managers
from datawinners.main.utils import create_views, sync_views
import mangrove
from mangrove.datastore.database import get_db_manager
from datawinners.location.utils import load_from_madagascar_ocha_wgs84_shp_file

class Command(BaseCommand):
    def handle(self, *args, **options):
        shape_file_dir = os.path.join(settings.PROJECT_DIR,"../../../shape_files/madawgs84/")
        load_from_madagascar_ocha_wgs84_shp_file(shape_file_dir,verbose=True)
