from django.conf.urls.defaults import patterns
from dataextraction.views import get_by_subject

urlpatterns = patterns('',
    (r'^api/get_by_subject/(?P<subject_type>.+?)/(?P<subject_id>.+?)/$', get_by_subject),
)