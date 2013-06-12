from django.forms import forms
from django.forms.fields import ChoiceField, CharField
from datawinners.activitylog.models import action_list
from django.utils.translation import ugettext_lazy as _
from datawinners.accountmanagement.models import NGOUserProfile
from datawinners.project.models import get_all_projects
from operator import itemgetter
from datawinners.main.database import get_database_manager

class LogFilterForm(forms.Form):
    user = ChoiceField(label=_('User'), choices=[], required=False)
    action = ChoiceField(label=_('Action'), choices=action_list, required=False)
    project = ChoiceField(label=_('Project'), choices=[])
    daterange = CharField(label=_("Date Range"), widget=forms.TextInput(attrs={'style':'width: 130px;', 'id':'dateRangePicker'}))

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        assert request is not None
        forms.Form.__init__(self, *args, **kwargs)
        org_id = request.user.get_profile().org_id

        users_rs = NGOUserProfile.objects.select_related().\
            extra(select={'lower_username': 'lower(auth_user.first_name)||lower(auth_user.last_name)'}).\
            filter(org_id=org_id).order_by("lower_username")

        all_users = [("",_("All Users"))]

        all_users.extend([(user.user.id, "%s %s" % (user.user.first_name.capitalize(),user.user.last_name.capitalize()))
            for user in users_rs])

        self.fields["user"].choices = all_users
        project_choices = [("", _("All Projects"))]
        projects = get_all_projects(get_database_manager(request.user))
        project_choices.extend(sorted([(prj["value"]["name"], prj["value"]["name"].capitalize()) for prj in projects],
                                    key=itemgetter(1,0)))
        self.fields["project"].choices = project_choices


