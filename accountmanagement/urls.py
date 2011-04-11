from django.conf.urls.defaults import patterns, include, url
from datawinners.accountmanagement.forms import RegistrationForm
from django.contrib import admin
admin.autodiscover()
from views import registration_complete, home
import datawinners.settings as settings


urlpatterns = patterns('',
#    (r'',include('datawinners.account.urls')),
#    (r'',include('datawinners.registration1.urls')),
    (r'^register$','registration.views.register',{'form_class':RegistrationForm,'template_name':'registration/register.html','backend':'datawinners.accountmanagement.registration_simple_backend.SimpleBackend'}),
    ('',include('registration.backends.default.urls')),
    (r'^registration_complete$',registration_complete),
    (r'^home$',home),
    # Examples:
    # url(r'^$', 'web.views.home', name='home'),
    # url(r'^web/', include('web.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)