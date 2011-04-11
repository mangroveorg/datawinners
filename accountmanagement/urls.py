from django.conf.urls.defaults import patterns, include, url
from datawinners.accountmanagement.forms import RegistrationForm, LoginForm, ResetPasswordForm, PasswordSetForm
from django.contrib import admin
admin.autodiscover()
from views import registration_complete, home
import datawinners.settings as settings
from django.contrib.auth import views as auth_views


urlpatterns = patterns('',
#    (r'',include('datawinners.account.urls')),
#    (r'',include('datawinners.registration1.urls')),
    (r'^register$','registration.views.register',{'form_class':RegistrationForm,'template_name':'registration/register.html','backend':'datawinners.accountmanagement.registration_simple_backend.SimpleBackend'}),
     url(r'^login/$',auth_views.login,{'template_name': 'registration/login.html','authentication_form': LoginForm},name='auth_login'),
     url(r'^password/reset/$',auth_views.password_reset,{'password_reset_form':ResetPasswordForm},name='auth_password_reset'),
     url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',auth_views.password_reset_confirm,{'set_password_form':PasswordSetForm},name='auth_password_reset_confirm'),
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