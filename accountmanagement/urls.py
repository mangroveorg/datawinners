# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.conf.urls.defaults import patterns, include, url
from datawinners.accountmanagement.forms import RegistrationForm, LoginForm, ResetPasswordForm, PasswordSetForm
from django.contrib import admin

admin.autodiscover()
from views import registration_complete, home
from django.contrib.auth import views as auth_views


urlpatterns = patterns('',
        (r'^register/$', 'registration.views.register',
             {'form_class': RegistrationForm, 'template_name': 'registration/register.html',
              'backend': 'datawinners.accountmanagement.registration_backend.RegistrationBackend'}),
                       url(r'^login/$', auth_views.login,
                               {'template_name': 'registration/login.html', 'authentication_form': LoginForm},
                           name='auth_login'),
                       url(r'^password/reset/$', auth_views.password_reset, {'password_reset_form': ResetPasswordForm},
                           name='auth_password_reset'),
                       url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
                           auth_views.password_reset_confirm, {'set_password_form': PasswordSetForm},
                           name='auth_password_reset_confirm'),
        ('', include('registration.backends.default.urls')),
        (r'^registration_complete$', registration_complete),
        (r'^home/$', home),
                       url(r'^admin/', include(admin.site.urls)),

                       )
