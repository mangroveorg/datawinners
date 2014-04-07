from collections import namedtuple

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from datawinners.entity.import_data import get_entity_type_info
from datawinners.project.utils import make_project_links, make_data_sender_links, make_subject_links
from mangrove.form_model.form_model import REPORTER


def get_form_context(questionnaire, survey_response_form, manager, hide_link_class, disable_link_class,entity_type=None, is_update=False):
    form_context = _make_form_context(survey_response_form, questionnaire, hide_link_class, disable_link_class, entity_type, is_update)
    form_context.update(_get_subject_info(manager, questionnaire, entity_type))

    return form_context


def add_link(project, entity_type=None):
    add_link_named_tuple = namedtuple("Add_Link", ['url', 'text'])
    if entity_type :
        text = _("Register a %(subject)s") % {'subject': entity_type}
        url = make_subject_links(project.id, entity_type)['register_subjects_link_web_view']
        return add_link_named_tuple(url=url, text=text)
    else:
        text = _("Add a data sender")
        url = make_data_sender_links(project.id)['register_datasenders_link']
        return add_link_named_tuple(url=url, text=text)


def _make_form_context(survey_response_form, form_model, hide_link_class, disable_link_class, entity_type=None, is_update=False):
    return {'questionnaire_form': survey_response_form,
            'project': form_model,
            'project_links': make_project_links(form_model, entity_type),
            'hide_link_class': hide_link_class,
            'disable_link_class': disable_link_class,
            'back_to_project_link': reverse("alldata_index"),
            'smart_phone_instruction_link': reverse("smart_phone_instruction"),
            'is_update': is_update
    }


def _get_subject_info(manager, project, entity_type=None):
    subject = get_entity_type_info(entity_type, manager=manager)
    subject_info = {'subject': subject,
                    'add_link': add_link(project, entity_type),
                    "entity_type": entity_type}
    return subject_info


def get_project_details_dict_for_feed(project):
    additional_feed_dictionary = {}
    project_details = {'id': project.id, 'name': project.name, 'type': project.entity_type[0] if len(project.entity_type) else ''}
    additional_feed_dictionary.update({'project': project_details})
    return additional_feed_dictionary


