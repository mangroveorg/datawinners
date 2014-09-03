from django.conf.urls.defaults import patterns
from datawinners.admin_apis.views import generate_token_for_datasender_activate

urlpatterns = patterns('',
                       (r'datasender/generate_token/$',generate_token_for_datasender_activate,
                       ))