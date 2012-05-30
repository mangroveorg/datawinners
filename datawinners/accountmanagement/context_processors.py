from django.conf import settings

def add_feature_flags(context):
    return {'TRIAL_REGISTRATION_ENABLED' : settings.TRIAL_REGISTRATION_ENABLED,
            'SHOW_GOOGLE_MAPS' : settings.SHOW_GOOGLE_MAPS,
            'DEBUG'  : settings.DEBUG,
            'SMARTPHONE_ENABLED'  : settings.SMARTPHONE_ENABLED,
            'refresh_rate': settings.REFRESH_RATE
            }

