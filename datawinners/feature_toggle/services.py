from datawinners.feature_toggle.models import FeatureSubscription
from waffle.models import Flag
import logging
from django.contrib.auth.models import User

logger = logging.getLogger("datawinners")

def handle_feature_toggle_impact_for_new_user(ngo_user_profile):
    try:
        org_id = ngo_user_profile.org_id
        feature_subscriptions = FeatureSubscription.objects.filter(organizations__org_id=org_id)
        if feature_subscriptions.exists():
            for feature_subscription in feature_subscriptions:
                flags = Flag.objects.filter(name=feature_subscription.feature.name)
                for flag in flags:
                    flag.users.add(ngo_user_profile.user)
    except Exception as e:
        logger.error('Unable to handle feature toggle impact for new users')

def handle_feature_toggle_impact_for_deleted_user(user_id):
    try:
        user = User.objects.get(id=user_id)      
        flags = Flag.objects.filter(users__id=user_id)
        for flag in flags:
            flag.users.remove(user)
    except Exception as e:
        logger.error("Unable to handle feature toggle for deleted user")
