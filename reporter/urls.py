from django.conf.urls.defaults import patterns
from datawinners.reporter.views import register

urlpatterns = patterns('',
    (r'^reporter/register', register),
)