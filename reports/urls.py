from django.conf.urls.defaults import patterns
from datawinners.reports.views import report

urlpatterns = patterns('',
    (r'^reports/reportperlocation', report),
)