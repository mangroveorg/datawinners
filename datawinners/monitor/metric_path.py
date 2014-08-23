from django.conf import settings

def create_path(name):
    return "%s.%s.%s" % ('dw', settings.ENVIRONMENT, name)