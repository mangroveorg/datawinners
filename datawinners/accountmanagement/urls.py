# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin

from datawinners.accountmanagement.forms import FullRegistrationForm, LoginForm, PasswordSetForm, MinimalRegistrationForm
from datawinners.accountmanagement.views import custom_reset_password
from views import settings, new_user, edit_user, users, custom_login, registration_complete, trial_expired, upgrade, delete_users, registration_activation_complete


admin.autodiscover()
from django.contrib.auth import views as auth_views


urlpatterns = patterns('',
                       (r'^register/$', 'registration.views.register',
                        {'form_class': FullRegistrationForm, 'template_name': 'registration/register.html',
                         'backend': 'datawinners.accountmanagement.registration_backend.RegistrationBackend'}),
                       (r'^register/trial/$', 'registration.views.register',
                        {'form_class': MinimalRegistrationForm, 'template_name': 'registration/register_for_trial.html',
                         'backend': 'datawinners.accountmanagement.registration_backend.RegistrationBackend'}),
                       url(r'^login/$', custom_login,
                           {'template_name': 'registration/login.html', 'authentication_form': LoginForm},
                           name='auth_login'),
                       url(r'^activate/complete/$',registration_activation_complete),
                           url(r'^password/reset/$', custom_reset_password, name='auth_password_reset'),
                       url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
                           auth_views.password_reset_confirm, {'set_password_form': PasswordSetForm},
                           name='auth_password_reset_confirm'),
                       url(r'^datasender/activate/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
                           auth_views.password_reset_confirm, {'set_password_form': PasswordSetForm,
                                                               'template_name':'registration/datasender_activate.html'},
                           name='activate_datasender_account'), 
                       ('', include('registration.backends.default.urls')),
                       (r'^registration_complete$', registration_complete),
                       url(r'^admin/', include(admin.site.urls)),
                       (r'^account/$', settings),
                       (r'^account/user/new/$', new_user),
                       (r'^profile/$', edit_user),
                       (r'^account/users/$', users),
                       (r'^account/users/delete/$', delete_users),
                       (r'^trial/expired/$', trial_expired),
                       (r'^upgrade/$', upgrade),
)
