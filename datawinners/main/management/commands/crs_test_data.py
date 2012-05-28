from django.core.management.base import BaseCommand
from datawinners.custom_reports.crs.test_data import create_one_set

class Command(BaseCommand):
    def handle(self, *args, **options):
        create_one_set()