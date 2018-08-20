# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enablSubscribe Nowe the admin:
# from django.contrib import admin
# admin.autodiscover()
import settings
from django.contrib import admin

js_info_dict = {
    'packages': ('datawinners',),
}

urlpatterns = patterns('',
                       (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
                       (r'', include('datawinners.accountmanagement.urls')),
                       (r'', include('datawinners.activitylog.urls')),
                       (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
                       (r'', include('datawinners.project.urls')),
                       (r'smstester/', include('datawinners.smstester.urls')),
                       (r'', include('datawinners.submission.urls')),
                       (r'', include('datawinners.public.urls')),
                       (r'', include('datawinners.dashboard.urls')),
                       (r'', include('datawinners.report.urls')),
                       (r'', include('datawinners.location.urls')),
                       (r'', include('datawinners.alldata.urls')),
                       (r'', include('datawinners.common.lang.urls')),
                       (r'^entity/', include('datawinners.entity.urls')),
                       (r'', include('datawinners.home.urls')),
                       (r'', include('datawinners.xforms.urls')),
                       (r'', include('datawinners.dataextraction.urls')),
                       (r'', include('datawinners.feeds.urls')),
                       (r'', include('datawinners.smsapi.urls')),
                       (r'', include('datawinners.submitapi.urls')),
                       (r'', include('datawinners.blue.urls')),
                       (r'', include('datawinners.feature_toggle_demo_advanced_dashboard.urls')),
                       (r'', include('datawinners.feature_toggle_demo_secured_endpoint.urls')),
                       url(r'^admin-apis/', include('datawinners.admin_apis.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       
)
