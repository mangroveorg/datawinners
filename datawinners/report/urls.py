from django.conf.urls.defaults import patterns, url

from datawinners.report.all_reports import AllReportsView, report_content

urlpatterns = patterns('',
                       url(r'reports/$', AllReportsView.as_view(), name='all_reports'),
                       url(r'^reports/(?P<report_id>.+?)/$', report_content)
                       )
