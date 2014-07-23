from django.core.urlresolvers import reverse
from mangrove.form_model.field import SelectField

from datawinners.entity.import_data import get_entity_type_info
from datawinners.project.utils import make_project_links


def get_form_context(questionnaire, survey_response_form, manager, hide_link_class, disable_link_class,entity_type=None, is_update=False):
    form_context = _make_form_context(survey_response_form, questionnaire, hide_link_class, disable_link_class, entity_type, is_update)
    form_context.update(_get_subject_info(manager, entity_type))

    return form_context


def _make_form_context(survey_response_form, form_model, hide_link_class, disable_link_class, entity_type=None, is_update=False):
    return {'questionnaire_form': survey_response_form,
            'project': form_model,
            'project_links': make_project_links(form_model, entity_type),
            'hide_link_class': hide_link_class,
            'disable_link_class': disable_link_class,
            'back_to_project_link': reverse("alldata_index"),
            'smart_phone_instruction_link': reverse("smart_phone_instruction", args=[form_model.id]),
            'is_update': is_update,
            'questionnaire_code': form_model.form_code
    }


def _get_subject_info(manager, entity_type=None):
    subject = get_entity_type_info(entity_type, manager=manager)
    subject_info = {'subject': subject,
                    "entity_type": entity_type}
    return subject_info


def get_project_details_dict_for_feed(project):
    additional_feed_dictionary = {}
    project_details = {'id': project.id, 'name': project.name, 'type': project.entity_type[0] if len(project.entity_type) else ''}
    additional_feed_dictionary.update({'project': project_details})
    return additional_feed_dictionary



def is_original_question_changed_from_choice_answer_type(original_field, latest_field):
    return isinstance(original_field, SelectField) and not isinstance(latest_field, SelectField)

def is_original_field_and_latest_field_of_type_choice_answer(original_field, latest_field):
    return isinstance(original_field, SelectField) and isinstance(latest_field, SelectField)

def convert_choice_options_to_options_text(field, answer):
    options = field.get_options_map()
    value_list = []
    for answer_value in list(answer):
        value_list.append(options[answer_value])
    return ",".join(value_list)

def filter_submission_choice_options_based_on_current_answer_choices(answer, original_field, latest_field):
    original_value_list = list(answer)
    original_option_map = original_field.get_options_map()
    latest_option_map = latest_field.get_options_map()
    new_value_list = []
    for item in original_value_list:
        if original_option_map.get(item) == latest_option_map.get(item):
            new_value_list.append(item)
    return "".join(new_value_list)