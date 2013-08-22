from collections import namedtuple

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from datawinners.entity.import_data import get_entity_type_info
from datawinners.project.utils import make_project_links, make_data_sender_links, make_subject_links
from mangrove.form_model.form_model import REPORTER


def get_form_context(form_code, project, questionnaire_form, manager, hide_link_class, disable_link_class,
                     is_update=False):
    form_context = _make_form_context(questionnaire_form, project, form_code, hide_link_class, disable_link_class,
                                      is_update)
    form_context.update(_get_subject_info(manager, project))

    return form_context


def add_link(project):
    add_link_named_tuple = namedtuple("Add_Link", ['url', 'text'])
    if project.entity_type == REPORTER:
        text = _("Add a data sender")
        url = make_data_sender_links(project.id)['register_datasenders_link']
        return add_link_named_tuple(url=url, text=text)
    else:
        text = _("Register a %(subject)s") % {'subject': project.entity_type}
        url = make_subject_links(project.id)['register_subjects_link']
        return add_link_named_tuple(url=url, text=text)


def _make_form_context(questionnaire_form, project, form_code, hide_link_class, disable_link_class, is_update=False):
    return {'questionnaire_form': questionnaire_form,
            'project': project,
            'project_links': make_project_links(project, form_code),
            'hide_link_class': hide_link_class,
            'disable_link_class': disable_link_class,
            'back_to_project_link': reverse("alldata_index"),
            'smart_phone_instruction_link': reverse("smart_phone_instruction"),
            'is_update': is_update
    }


def _get_subject_info(manager, project):
    subject = get_entity_type_info(project.entity_type, manager=manager)
    subject_info = {'subject': subject,
                    'add_link': add_link(project),
                    "entity_type": project.entity_type}
    return subject_info


def get_project_details_dict_for_feed(project):
    additional_feed_dictionary = {}
    project_details = {'id': project.id, 'name': project.name, 'type': project.entity_type,
                       'status': project.state}
    additional_feed_dictionary.update({'project': project_details})
    return additional_feed_dictionary


