import logging
from datawinners.accountmanagement.models import Organization


class ExceptionMiddleware(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_exception(self, request, exception):
        try:
            profile = request.user.get_profile()
            organization = Organization.objects.get(org_id=profile.org_id)
            request.META['organization_details'] = ('%s (%s)' % (organization.name, profile.org_id))
            request.META['user_email_id'] = request.user.username
        except Exception as ex:
            self.logger.error("error while getting meta info to be provided via email", ex)
        return None

