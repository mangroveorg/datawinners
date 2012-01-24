from django.core.management.base import BaseCommand
import os
from django.conf import settings
from datawinners.location.utils import load_from_madagascar_ocha_wgs84_shp_file

class Command(BaseCommand):
    def handle(self, *args, **options):
        shape_file_dir = os.path.join(settings.PROJECT_DIR, "../../shape_files/madawgs84/")
        load_from_madagascar_ocha_wgs84_shp_file(shape_file_dir, verbose=True)
