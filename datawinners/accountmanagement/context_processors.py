from django.conf import settings

def add_feature_flags(context):
    return {'TRIAL_REGISTRATION_ENABLED' : settings.TRIAL_REGISTRATION_ENABLED,
            'GOOGLE_MAPS_ENABLED': settings.GOOGLE_MAPS_ENABLED,
            'GOOGLE_ANALYTICS_ENABLED': settings.GOOGLE_ANALYTICS_ENABLED,
            'DEBUG'  : settings.DEBUG,
            'EDIT_SUBJECT_ENABLED'  : settings.EDIT_SUBJECT_ENABLED,
            'EDIT_DATA_SENDERS_ENABLED'  : settings.EDIT_DATA_SENDERS_ENABLED,
            'refresh_rate': settings.REFRESH_RATE
            }

