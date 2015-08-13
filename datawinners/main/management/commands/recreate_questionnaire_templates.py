from django.core.management.base import BaseCommand
from datawinners.main.initial_template_creation import create_questionnaire_templates


class Command(BaseCommand):
    def handle(self, *args, **options):
        print "Creating questionnnaire templates..."
        create_questionnaire_templates()


