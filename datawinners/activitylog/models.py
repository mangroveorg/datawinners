from django.db import models
from datawinners.activitylog.html_views import EditedDataSubmissionView, EditedRegistrationFormView, EditedProjectView
from django.contrib.auth.models import User
from datetime import datetime
from django.utils.translation import ugettext_lazy as _, ugettext
import json
from datawinners.common.constant import *

action_list = (
    ('',_("All Actions")),
        
    (_('Account Administration'), (
        (ADDED_USER, _(ADDED_USER)),
        (CHANGED_ACCOUNT_INFO, _(CHANGED_ACCOUNT_INFO)),
        (DELETED_USERS, _(DELETED_USERS)),
    )),

    (_('Questionnaire'),(
        (CREATED_QUESTIONNAIRE, _(CREATED_QUESTIONNAIRE)),
        (ACTIVATED_QUESTIONNAIRE, _(ACTIVATED_QUESTIONNAIRE)),
        (EDITED_QUESTIONNAIRE, _(EDITED_QUESTIONNAIRE)),
        (DELETED_QUESTIONNAIRE, _(DELETED_QUESTIONNAIRE))
    )),

    (_("Identification Number"),(
        (ADDED_IDENTIFICATION_NUMBER_TYPE, _(ADDED_IDENTIFICATION_NUMBER_TYPE)),
        (EDITED_REGISTRATION_FORM, _(EDITED_REGISTRATION_FORM)),
        (REGISTERED_IDENTIFICATION_NUMBER, _(REGISTERED_IDENTIFICATION_NUMBER)),
        (IMPORTED_IDENTIFICATION_NUMBER, _(IMPORTED_IDENTIFICATION_NUMBER)),
        (DELETED_IDENTIFICATION_NUMBER, _(DELETED_IDENTIFICATION_NUMBER)),
    )),

    (_("Data Senders"),(
        (REGISTERED_DATA_SENDER, _(REGISTERED_DATA_SENDER)),
        (IMPORTED_DATA_SENDERS, _(IMPORTED_DATA_SENDERS)),
        (EDITED_DATA_SENDER, _(EDITED_DATA_SENDER)),
        (DELETED_DATA_SENDERS, _(DELETED_DATA_SENDERS)),
        (ADDED_DATA_SENDERS_TO_PROJECTS, _(ADDED_DATA_SENDERS_TO_PROJECTS)),
        (REMOVED_DATA_SENDER_TO_PROJECTS, _(REMOVED_DATA_SENDER_TO_PROJECTS)),
    )),

    (_("Data Submissions"),(
        (DELETED_DATA_SUBMISSION, _(DELETED_DATA_SUBMISSION)),
        (EDITED_DATA_SUBMISSION, _(EDITED_DATA_SUBMISSION)),
    )),

    (_("Reminders"),(
        (ACTIVATED_REMINDERS, _(ACTIVATED_REMINDERS)),
        (DEACTIVATED_REMINDERS, _(DEACTIVATED_REMINDERS)),
        (SET_DEADLINE, _(SET_DEADLINE)),
    ))
)

_mapping_dict = {EDITED_REGISTRATION_FORM: EditedRegistrationFormView,
                EDITED_QUESTIONNAIRE: EditedProjectView,
                EDITED_DATA_SUBMISSION: EditedDataSubmissionView}


class UserActivityLog(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    organization = models.TextField(max_length=40)
    detail = models.TextField()
    action = models.TextField(choices=action_list)
    project = models.TextField()
    log_date = models.DateTimeField(auto_now_add=True)

    def log(self, request, *args, **kwargs):
        from datawinners.utils import get_organization
        ong = get_organization(request)
        user = request.user
        entry = UserActivityLog(user=user, organization=ong.org_id, *args, **kwargs)
        entry.save()

    def translated_action(self):
        return ugettext(self.action)

    def translated_detail(self):
        try:
            detail_dict = json.loads(self.detail)
            assert isinstance(detail_dict, dict)
        except Exception:
            return self.detail

        if _mapping_dict.has_key(self.action):
            detail_list = _mapping_dict[self.action](detail_dict).html()
        else:
            detail_list = "<br/>".join(self._get_detail(detail_dict))

        return detail_list

    def _get_detail(self, detail_dict):
        detail_list = []
        for key,changed in detail_dict.items():
            detail_list.append("%s: %s" % (ugettext(key),  changed))
        return detail_list

    def to_render(self):
        if self.user:
            name = "%s" % (self.user.first_name)
        else:
            name = ugettext("Deleted User")
        return [name, self.translated_action(),
                self.project, self.translated_detail(), datetime.strftime(self.log_date,  "%d.%m.%Y %R")]
