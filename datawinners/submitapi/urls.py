from django.conf.urls.defaults import patterns
from datawinners.submitapi.make_submission import  post_submission

urlpatterns = patterns('', (r'^api/post_submission/$', post_submission))
