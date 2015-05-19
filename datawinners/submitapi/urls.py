from django.conf.urls.defaults import patterns
from datawinners.submitapi.make_submission import  post_data

urlpatterns = patterns('', (r'^api/post-data/$', post_data))
