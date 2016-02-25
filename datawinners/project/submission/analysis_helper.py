import datetime
import logging
import json

from datawinners.search.index_utils import lookup_entity,\
    es_questionnaire_field_name
from datawinners.accountmanagement.localized_time import convert_utc_to_localized
from mangrove.form_model.form_model import get_form_model_by_entity_type, EntityFormModel
from __builtin__ import isinstance
from mangrove.form_model.field import FieldSet

logger = logging.getLogger("datawinners")

def enrich_analysis_data(record, questionnaire, submission_id, is_export=False):
    try:
        dbm = questionnaire._dbm
        if isinstance(questionnaire, EntityFormModel):
            entity_questions = questionnaire.base_entity_questions
        else:
            entity_questions = questionnaire.entity_questions

        linked_id_details = [_get_linked_id_details(dbm, field, parent_field_types=[]) for field in entity_questions]
        
        for linked_id_detail in linked_id_details:
            _update_record_with_linked_id_details(dbm, record, linked_id_detail, questionnaire.id,nested=False)
        
        if isinstance(record, dict):
            record_as_dict = record
        else:
            record_as_dict = record.to_dict()   
                
        for key, value in record_as_dict.iteritems():
            if isinstance(value, basestring):
                try:
                    value_obj = json.loads(value)
                    if isinstance(value_obj, list) and not is_export:
                        _transform_nested_question_answer(key, value_obj, record, questionnaire, submission_id)
                except Exception as e:
                    continue
    except Exception as ex:
        logger.exception('Unable to enrich analysis data')
        
    return record

def _get_linked_id_details(dbm, field, parent_field_types=[]):
    try:
        linked_id_details = []
        if field.unique_id_type in parent_field_types:
            return None #Prevent cyclic Linked ID Nr
        parent_field_types.append(field.unique_id_type)
        id_number_fields = get_form_model_by_entity_type(dbm, [field.unique_id_type]).fields
        linked_id_fields = [child_field for child_field in id_number_fields if child_field.type in ['unique_id']]
        if linked_id_fields:
            for linked_id_field in linked_id_fields:
                if linked_id_field.unique_id_type in parent_field_types:
                    continue
                linked_id_info = {
                    'code':field.code,
                    'type':field.unique_id_type,
                    'parent_code': field.parent_field_code,
                    'linked_code':linked_id_field.code,
                    'linked_type':linked_id_field.unique_id_type
                }
                linked_id_info['children'] = _get_linked_id_details(dbm, linked_id_field, parent_field_types=parent_field_types)
                linked_id_details.append(linked_id_info)
        return linked_id_details
    except Exception as e:
        logger.exception("Exception in constructing linked id hierrachy : \n%s" % e)
        return None

def _update_record_with_linked_id_details(dbm, record, linked_id_detail, questionnaire_id, nested=False):
    try:
        for linked_id_info in linked_id_detail:
            if nested:
                base_node = record
            else:
                code = linked_id_info['parent_code'] + '-' + linked_id_info['code'] if linked_id_info['parent_code'] else linked_id_info['code']
                base_node = record[questionnaire_id+'_'+code+'_details']
            
            value = base_node[linked_id_info['linked_code']]
            linked_entity = lookup_entity(dbm, value, [linked_id_info['linked_type']])
            base_node[linked_id_info['linked_code']+'_details'] = linked_entity
            if linked_id_info['children']:
                _update_record_with_linked_id_details(
                                                      dbm, 
                                                      base_node[linked_id_info['linked_code']+'_details'], 
                                                      linked_id_info['children'], questionnaire_id,nested=True)
    except KeyError as key_err:
        return #When linked ID doesn't have value, this happens and displays blank in view
    except Exception as e:
        logger.exception("Exception in constructing linked id info : \n%s" % e)
        return

def _transform_nested_question_answer(key, value_obj, record, questionnaire, submission_id):
    from datawinners.search.submission_query import format_fieldset_values_for_representation
    field_set_fields = get_field_set_fields(questionnaire.id, questionnaire.fields)
    target_field = field_set_fields.get(key)
    updated_answers = format_fieldset_values_for_representation(value_obj, target_field, submission_id)
    record[key] = updated_answers

def convert_to_localized_date_time(submission_date, local_time_delta):
    submission_date_time = datetime.datetime.strptime(submission_date, "%b. %d, %Y, %I:%M %p")
    datetime_local = convert_utc_to_localized(local_time_delta, submission_date_time)
    return datetime_local.strftime("%b. %d, %Y, %H:%M")

def get_field_set_fields(form_model_id, fields, parent_field_code=None):
    field_set_field_dict = {}
    for field in fields:
        if isinstance(field, FieldSet):
            field_set_field_dict.update(
                {es_questionnaire_field_name(field.code, form_model_id, parent_field_code): field})
            group_field_code = field.code if field.is_group() else None
            field_set_field_dict.update(get_field_set_fields(form_model_id, field.fields, group_field_code))
    return field_set_field_dict
    
