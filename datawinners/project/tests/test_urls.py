import unittest
import os, re
import settings
from django.core import urlresolvers
from project.views import project_data

class TestUrl(unittest.TestCase):
    def view_to_str(self, view):
        filename = view.func_code.co_filename
        app_dir = filename.replace(settings.PROJECT_DIR, '')
        project_name = os.path.basename(settings.PROJECT_DIR)
        app_name, view_module = re.findall(r'/(\w+)/(\w+).py', app_dir)[0]
        return '%s.%s.%s.%s' % (project_name, app_name, view_module, view.func_name)

    def assert_url_match(self, result, kwargs):
        urlresolvers_reverse = urlresolvers.reverse(self.view_to_str(project_data),
            kwargs=kwargs)
        self.assertEquals(result, urlresolvers_reverse)