from django.conf.urls.defaults import patterns
from datawinners.admin_apis.views import generate_token_for_datasender_activate, \
    check_if_datasender_entry_made_in_postgres

urlpatterns = patterns('',
                       (r'datasender/generate_token/$',generate_token_for_datasender_activate),
                       (r'datasender/check_if_entry_made_in_postgres/$',check_if_datasender_entry_made_in_postgres),
                       )