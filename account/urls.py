from django.conf.urls.defaults import *
from views import settings, new_user

urlpatterns = patterns('',
                       (r'^account/$',settings),
                       (r'^account/user/new/$', new_user),
                       )
