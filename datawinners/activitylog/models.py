from django.db import models
from datawinners.accountmanagement.models import Organization
from django.contrib.auth.models import User
from datetime import datetime
from django.utils.translation import ugettext_lazy as _, ugettext
import json

action_list = (
    ('',_("All Actions")),
        
    (_('Account Administration'), (
        ('Added User', _('Added User')),
        ('Changed Account Information', _('Changed Account Information'))
    )),

    (_('Project'),(
        ('Created Project', _('Created Project')),
        ('Activated Project', _('Activated Project')),
        ('Deleted Project', _('Deleted Project'))
    )),

    (_("Subjects"),(
        ("Added Subject Type", _("Added Subject Type")),
        ("Edited Registration Form", _("Edited Registration Form")),
        ("Registered Subject", _("Registered Subject")),
        ("Imported Subjects", _("Imported Subjects")),
        ("Deleted Subjects", _("Deleted Subjects")),
    )),

    (_("Data Senders"),(
        ("Registered Data Sender", _("Registered Data Sender")),
        ("Imported Data Senders", _("Imported Data Senders")),
        ("Edited Data Sender", _("Edited Data Sender")),
        ("Deleted Data Senders", _("Deleted Data Senders")),
        ("Added Data Senders to Projects", _("Added Data Senders to Projects")),
        ("Removed Data Sender from Project", _("Removed Data Sender from Project")),
    )),

    (_("Data Submissions"),(
        ("Deleted Data Submission", _("Deleted Data Submission")),
    )),

    (_("Reminders"),(
        ("Activated Reminders", _("Activated Reminders")),
        ("De-Activated Reminders", _("De-Activated Reminders")),
        ("Set Deadline", _("Set Deadline")),
    ))
)

class UserActivityLog(models.Model):
    user = models.ForeignKey(User)
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
        return "%s" % ugettext(self.action)

    def translated_detail(self):
        try:
            detail_dict = json.loads(self.detail)
        except Exception:
            return self.detail
        
        if self.action == "Edited Registration Form":
            detail_list = []
            try:
                detail_list.append( "%s: %s" % (ugettext("Subject Type"), detail_dict["entity_type"]))
            except KeyError:
                pass

            try:
                detail_list.append( "%s: %s" % (ugettext("Questionnaire Code"), detail_dict["form_code"]))
            except KeyError:
                pass

            for type in ["added", "deleted"]:
                try:
                    str = '<ul class="bulleted">'
                    for item in detail_dict[type]:
                        str += "<li>%s</li>" % item
                    str += "</ul>"
                    detail_list.append( "%s: %s" % (ugettext("%s Questions" % type.capitalize()), str))
                except KeyError:
                    pass

            try:
                str = '<ul class="bulleted">'
                for changed in detail_dict["changed"]:
                    str += "<li>%s</li>" % changed
                str += "</ul>"
                detail_list.append("%s: %s" % (ugettext("Questions Labels Changed"), str))
            except KeyError:
                pass

            try:
                for type_changed in detail_dict["changed_type"]:
                    detail_dict.append(ugettext('Answer type changed to %(answer_type)s for \"%(question_label)s\"' %
                                                (type_changed.type, type_changed.label)))
            except KeyError:
                pass

            return "<br/>".join(detail_list)
            
        else: #self.action.find("Changed") != -1 or self.action.find("Edited") != -1:
            detail_list = []
            for key,changed in detail_dict.items():
                detail_list.append("%s: %s" % (ugettext(key),  changed))
            return "<br/>".join(detail_list)

    def to_render(self):
        return ["%s %s" % (self.user.first_name.capitalize(), self.user.last_name.capitalize()), self.translated_action(),
                self.project.capitalize(), self.translated_detail(), datetime.strftime(self.log_date,  "%d.%m.%Y %R")]
