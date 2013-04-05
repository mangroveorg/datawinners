from django.db import models
from datawinners.accountmanagement.models import Organization
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

    (_('Project'),(
        (CREATED_PROJECT, _(CREATED_PROJECT)),
        (ACTIVATED_PROJECT, _(ACTIVATED_PROJECT)),
        (EDITED_PROJECT, _(EDITED_PROJECT)),
        (DELETED_PROJECT, _(DELETED_PROJECT))
    )),

    (_("Subjects"),(
        (ADDED_SUBJECT_TYPE, _(ADDED_SUBJECT_TYPE)),
        (EDITED_REGISTRATION_FORM, _(EDITED_REGISTRATION_FORM)),
        (REGISTERED_SUBJECT, _(REGISTERED_SUBJECT)),
        (IMPORTED_SUBJECTS, _(IMPORTED_SUBJECTS)),
        (DELETED_SUBJECTS, _(DELETED_SUBJECTS)),
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
        
        if self.action == "Edited Registration Form":
            detail_list = []
            if "entity_type" in detail_dict:
                detail_list.append( "%s: %s" % (ugettext("Subject Type"), detail_dict["entity_type"]))

            if "form_code" in detail_dict:
                detail_list.append( "%s: %s" % (ugettext("Questionnaire Code"), detail_dict["form_code"]))

            detail_list.append(self._get_questionnaire_detail(detail_dict))

        elif self.action == "Edited Project" :
            questionnaire_detail = [self._get_questionnaire_detail(detail_dict)]
            for type in ["changed","added","changed_type", "deleted"]:
                try:
                    detail_dict.pop(type)
                except:
                    pass
            detail_list = self._get_detail(detail_dict)
            detail_list.extend(questionnaire_detail)
        else:
            detail_list = self._get_detail(detail_dict)
        return "<br/>".join(detail_list)

    def _get_questionnaire_detail(self, detail_dict):
        detail_list = []
        for type in ["added", "deleted"]:
            if type in detail_dict:
                str = '<ul class="bulleted">'
                for item in detail_dict[type]:
                    str += "<li>%s</li>" % item
                str += "</ul>"
                detail_list.append( "%s: %s" % (ugettext("%s Questions" % type.capitalize()), str))

        if "changed" in detail_dict:
            str = '<ul class="bulleted">'
            for changed in detail_dict["changed"]:
                if changed is not None:
                    str += "<li>%s</li>" % changed
            str += "</ul>"
            detail_list.append("%s: %s" % (ugettext("Question Labels Changed"), str))

        if "changed_type" in detail_dict:
            response_type = {"select1": "List of Choices", "select": "List of Choices", "text": "Word or Phrase", "integer":"Number",
                             "geocode": "GPS Coordinates", "date": "date", "telephone_number": "Telephone Number"}
            for type_changed in detail_dict["changed_type"]:
                detail_list.append(ugettext('Answer type changed to %(answer_type)s for \"%(question_label)s\"') %
                                            {"answer_type":ugettext(response_type.get(type_changed["type"], "")), "question_label":type_changed["label"]})
                
        return "<br/>".join(detail_list)

    def _get_detail(self, detail_dict):
        detail_list = []
        for key,changed in detail_dict.items():
            detail_list.append("%s: %s" % (ugettext(key),  changed))
        return detail_list

    def to_render(self):
        if self.user:
            name = "%s %s" % (self.user.first_name.capitalize() , self.user.last_name.capitalize())
        else:
            name = ugettext("Deleted User")
        return [name, self.translated_action(),
                self.project.capitalize(), self.translated_detail(), datetime.strftime(self.log_date,  "%d.%m.%Y %R")]
