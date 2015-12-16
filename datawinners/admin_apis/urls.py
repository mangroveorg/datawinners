from django.conf.urls.defaults import patterns
from datawinners.admin_apis.views import generate_token_for_datasender_activate, \
    check_if_datasender_entry_made_in_postgres, check_if_message_is_there_in_postgres,\
    reindex, list_of_indexes_out_of_sync, start_reindex, reindex_status

urlpatterns = patterns('',
                       (r'datasender/generate_token/$',generate_token_for_datasender_activate),
                       (r'datasender/check_if_entry_made_in_postgres/$',check_if_datasender_entry_made_in_postgres),
                       (r'sendamessage/check_if_message_present_in_postgres/$',check_if_message_is_there_in_postgres),
                       (r'reindex/list/$',list_of_indexes_out_of_sync),
                       (r'reindex/start_reindex/$',start_reindex),
                       (r'reindex/status/$',reindex_status),
                       (r'reindex/$',reindex),
                       )