import datetime
import logging
import json

from datawinners.search.index_utils import lookup_entity
from datawinners.accountmanagement.localized_time import get_country_time_delta, convert_utc_to_localized
from mangrove.form_model.form_model import get_form_model_by_entity_type
from __builtin__ import isinstance

logger = logging.getLogger("datawinners")

def enrich_analysis_data(record, questionnaire):
    try:
        dbm = questionnaire._dbm
        unique_id_fields = [field for field in questionnaire.fields if field.type in ['unique_id']]
        linked_id_details = [_get_linked_id_details(dbm, field, parent_field_types=[]) for field in unique_id_fields]
        
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
                    if isinstance(value_obj, list):
                        _transform_nested_question_answer(key, value_obj, record, questionnaire)
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
        if (linked_id_fields):
            for linked_id_field in linked_id_fields:
                if linked_id_field.unique_id_type in parent_field_types:
                    continue
                linked_id_info = {
                                  'code':field.code, 
                                  'type':field.unique_id_type,
                                  'linked_code':linked_id_field.code,
                                  'linked_type':linked_id_field.unique_id_type,
                                  }
                linked_id_info['children'] = _get_linked_id_details(dbm, linked_id_field, parent_field_types=parent_field_types)
                linked_id_details.append(linked_id_info)
        return linked_id_details
    except Exception as e:
        logger.exception("Exception in constructing linked id hierrachy : \n%s" % e)
        return None

def _update_record_with_linked_id_details(dbm, record, linked_id_detail, questionnaire_id, nested=False):
    try:
        
        if linked_id_detail is None:
            return 
        
        for linked_id_info in linked_id_detail:
            if nested:
                base_node = record
            else:
                base_node = record[questionnaire_id+'_'+linked_id_info['code']+'_details']
            
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


def _transform_nested_question_answer(key, value_obj, record, questionnaire):
    field_code = key.replace(record.meta.doc_type + '_', '')
    target_fields = [nested_field for nested_field in questionnaire.has_nested_fields if
                     nested_field.code == field_code]
    updated_answers = ''
    for repeat_question_answer in value_obj:
        updated_answer = ''
        for field in target_fields[0].fields:
            field_value = repeat_question_answer[field.code] if repeat_question_answer[field.code] else ''
            str_value = _handle_field_types(field, field_value, record.meta.id, repeat_question_answer)

            updated_answer += '<div><span>' + field.label + '</span><div>' + str_value + '</div></div>'
            updated_answer += ' '
        updated_answers += updated_answer + ';<br/><br/>'

    record[key] = updated_answers


def _handle_field_types(field, field_value, submission_id, repeat_question_answer):
    str_value = ''
    if field.type == 'photo':
        str_value = "<a href='/download/attachment/%s/%s'><img src='/download/attachment/%s/preview_%s' " \
                    "alt=''/></a><br>" % (submission_id, field_value, submission_id, field_value)
    elif field.type in ['audio', 'video']:
        str_value = "<a href='/download/attachment/%s/%s'>%s</a>" % (submission_id, field_value, field_value)
    elif isinstance(field_value, list) and not field.type == 'field_set':
        str_value = ','.join(field_value)
    elif field.type == 'field_set':
        sub_question_answer = repeat_question_answer[field.code] if repeat_question_answer[field.code] else ''
        for answer in sub_question_answer:
            for f in field.fields:
                field_value = answer[f.code] if answer[f.code] else None
                try:
                    if field_value:
                        return _handle_field_types(f, field_value, submission_id, answer)
                except Exception as e:
                    pass
    else:
        str_value = field_value
    return str_value

def convert_to_localized_date_time(submission_date, local_time_delta):
    submission_date_time = datetime.datetime.strptime(submission_date, "%b. %d, %Y, %I:%M %p")
    datetime_local = convert_utc_to_localized(local_time_delta, submission_date_time)
    return datetime_local.strftime("%b. %d, %Y, %H:%M")


