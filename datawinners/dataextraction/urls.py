from django.conf.urls.defaults import patterns
from dataextraction.views import get_for_subject

urlpatterns = patterns('',
    (r'^api/get_for_subject/(?P<subject_type>\w+?)/(?P<subject_id>\w+?)/$', get_for_subject),
    (r'^api/get_for_subject/(?P<subject_type>\w+?)/(?P<subject_id>\w+?)/(?P<start_date>[-0-9]+?)/$', get_for_subject),
    (r'^api/get_for_subject/(?P<subject_type>\w+?)/(?P<subject_id>\w+?)/(?P<start_date>[-0-9]+?)/(?P<end_date>[-0-9]+?)/$', get_for_subject),
)