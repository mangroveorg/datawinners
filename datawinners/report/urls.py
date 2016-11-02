from django.conf.urls.defaults import patterns, url

from datawinners.report.all_reports import AllReportsView

urlpatterns = patterns('',
                       url(r'reports/$', AllReportsView.as_view(), name='all_reports')
                       )