import logging
from datawinners.accountmanagement.models import Organization


class ExceptionMiddleware(object):
    def __init__(self):
        self.logger = logging.getLogger('datawinners')

    def process_exception(self, request, exception):
        try:
            self.logger.exception('Exception occurred')
            request.META['user_email_id'] = request.user.username
            profile = request.user.get_profile()
            organization = Organization.objects.get(org_id=profile.org_id)
            request.META['organization_details'] = ('%s (%s)' % (organization.name, profile.org_id))
            self.logger.exception("Exception happened for request "+request.path)
        except Exception as ex:
            pass
        return None

