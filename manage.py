# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
#!/usr/bin/env python
from django.core.management import execute_manager, setup_environ
import imp
import sys
import os

try:
    imp.find_module('settings') # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
    sys.exit(1)

import settings

# setup the environment before we start accessing things in the settings.
setup_environ(settings)
sys.path.append(os.path.join(settings.PROJECT_DIR, '../../src'))

if __name__ == "__main__":
    execute_manager(settings)
