from django.conf import settings

def add_feature_flags(context):
    return {'TRIAL_REGISTRATION_ENABLED' : settings.TRIAL_REGISTRATION_ENABLED}
  