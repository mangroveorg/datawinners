import os
from django.core.management import BaseCommand
from pathlib import Path
import scss
from datawinners import settings


def compile(root_directory):
    print root_directory
    for dirname, subdirs, files in os.walk(root_directory):
        for file in files:
            if file.endswith(".scss"):
                compiled_css_content = scss.compiler.compile_file(file, root=Path(root_directory))
                fo = open(root_directory + os.path.splitext(file)[0]+".css", "w+")
                fo.write(compiled_css_content)
        if subdirs.__len__():
            for dir in subdirs:
                compile(root_directory+dir+'/')


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            compile(settings.SCSS_COMPILE_PATH)
        except Exception as e:
            print e.message