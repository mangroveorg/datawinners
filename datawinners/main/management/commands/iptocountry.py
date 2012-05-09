from django.core.management.base import BaseCommand
from subprocess import call

class Command(BaseCommand):
    def handle(self, *args, **options):
        db_url = 'http://www.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz'
        gz_file = db_url.split('/')[-1]
        call(['wget', db_url])
        call(['gunzip', gz_file])
        call(['mv', 'GeoIP.dat', '../../'])
        call(['rm', gz_file])