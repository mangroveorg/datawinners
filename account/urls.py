from django.conf.urls.defaults import *
from views import settings, new_user, users, edit_user

urlpatterns = patterns('',
        (r'^account/$', settings),
        (r'^account/user/new/$', new_user),
        (r'^account/user/edit/$', edit_user),
        (r'^account/users/$', users),
                       )
