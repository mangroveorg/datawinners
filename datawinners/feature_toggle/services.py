from datawinners.feature_toggle.models import FeatureSubscription
from waffle.models import Flag
import logging

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
        