import json
import logging
from collections import OrderedDict
from types import NoneType

from babel.dates import format_datetime
import elasticutils
from pyelasticsearch.exceptions import ElasticHttpError, ElasticHttpNotFoundError

from datawinners.project.couch_view_helper import get_all_projects
from datawinners.project.views.utils import is_original_question_changed_from_choice_answer_type, \
    convert_choice_options_to_options_text
from datawinners.settings import ELASTIC_SEARCH_URL, ELASTIC_SEARCH_TIMEOUT
from mangrove.datastore.documents import ProjectDocument
from datawinners.search.submission_index_meta_fields import submission_meta_fields
from mangrove.form_model.field import DateField, UniqueIdField, SelectField, FieldSet, SelectOneExternalField
from datawinners.search.submission_index_constants import SubmissionIndexConstants
from datawinners.search.submission_index_helper import SubmissionIndexUpdateHandler
from mangrove.errors.MangroveException import DataObjectNotFound
from datawinners.search.index_utils import get_elasticsearch_handle, get_field_definition, _add_date_field_mapping, \
    es_unique_id_code_field_name, \
    es_questionnaire_field_name, _add_text_field_mapping, es_unique_id_details_field_name,\
    lookup_entity, get_field_definition_with_binary_type, _add_binary_field_mapping
from mangrove.datastore.entity import get_by_short_code_include_voided, Entity, Contact
from mangrove.form_model.form_model import FormModel, get_form_model_by_entity_type
from mangrove.form_model.project import Project
from mangrove.form_model.field import PhotoField, AudioField, VideoField

logger = logging.getLogger("datawinners")
UNKNOWN = "N/A"
ES_NUMBER_OF_TYPES_SUPPORTED = 115


def get_code_from_es_field_name(es_field_name, form_model_id):
    for item in es_field_name.split('_'):
        if item != 'value' and item != form_model_id:
            return item


def create_submission_mapping(dbm, latest_form_model, old_form_model):
    SubmissionSearchStore(dbm, latest_form_model, old_form_model).update_store()


class SubmissionSearchStore():
    def __init__(self, dbm, latest_form_model, old_form_model):
        self.dbm = dbm
        self.es = get_elasticsearch_handle()
        self.latest_form_model = latest_form_model
        self.old_form_model = old_form_model

    def update_store(self):
        mapping = self.get_mappings()
        try:
            mapping_old = self.get_old_mappings()
            if mapping_old:
                self._verify_change_involving_date_field(mapping, mapping_old)
                self._verify_unique_id_change()
            if not mapping_old or self._has_fields_changed(mapping, mapping_old):
                self.es.put_mapping(self.dbm.database_name, self.latest_form_model.id, mapping)

        except (ElasticHttpError, FieldTypeChangeException) as e:
            if isinstance(e, FieldTypeChangeException) or e[1].startswith('MergeMappingException'):
                self.recreate_and_populate_elastic_store()
            else:
                logger.error(e)
        except Exception as e:
            logger.error(e)

    def is_mapping_out_of_sync(self):
        try:
            mapping = self.get_mappings()
            mapping_old = self.get_old_mappings()
            if mapping_old:
                self._verify_change_involving_date_field(mapping, mapping_old)
                self._verify_unique_id_change()
            return not mapping_old or self._has_fields_changed(mapping, mapping_old)
        except Exception as e:
            return True
        
    def _has_fields_changed(self, mapping, mapping_old):
        old_mapping_properties = mapping_old.values()[0].values()[0].values()[0]['properties']
        new_fields_with_format = set(
            [k + f["fields"][k + "_value"]["type"] for k, f in mapping.values()[0]['properties'].items() if f.get('fields')])
        old_fields_with_format = set(
            [k + f["fields"][k + "_value"]["type"] for k, f in old_mapping_properties.items() if
             f.get("fields")])

        return new_fields_with_format != old_fields_with_format

    def _verify_change_involving_date_field(self, mapping, mapping_old):
        old_mapping_properties = mapping_old.values()[0].values()[0].values()[0]['properties']
        new_mapping_properties = mapping.values()[0]['properties']
        old_q_codes = old_mapping_properties.keys()
        new_q_codes = new_mapping_properties.keys()
        new_date_fields_with_format = set(
            [k + f["fields"][k + "_value"]["format"] for k, f in new_mapping_properties.items()
             if f.get('fields') and f["fields"][k + "_value"]["type"] == "date" and k in old_q_codes])
        old_date_fields_with_format = set(
            [k + f["fields"][k + "_value"]["format"] for k, f in old_mapping_properties.items()
             if f.get('fields') and f["fields"][k + "_value"]["type"] == "date" and k in new_q_codes])
        date_format_changed = old_date_fields_with_format != new_date_fields_with_format
        if date_format_changed:
            raise FieldTypeChangeException()

    def get_old_mappings(self):
        mapping_old = []
        try:
            mapping_old = self.es.get_mapping(index=self.dbm.database_name, doc_type=self.latest_form_model.id)
        except ElasticHttpNotFoundError as e:
            pass
        return mapping_old

    def get_mappings(self):
        fields_definition = []
        fields_definition.extend(get_submission_meta_fields())
        self._get_submission_fields(fields_definition, self.latest_form_model.fields)
        mapping = self.get_fields_mapping_by_field_def(doc_type=self.latest_form_model.id,
                                                       fields_definition=fields_definition)
        return mapping

    def _get_submission_fields(self, fields_definition, fields, parent_field_name=None):
        for field in fields:
            if isinstance(field, UniqueIdField):
                unique_id_field_name = es_questionnaire_field_name(field.code, self.latest_form_model.id,
                                                                   parent_field_name)
                fields_definition.append(
                    get_field_definition(field, field_name=es_unique_id_code_field_name(unique_id_field_name)))

            if isinstance(field, FieldSet):
                if field.is_group():
                    self._get_submission_fields(fields_definition, field.fields, field.code)
                else:
                    es_field_name = es_questionnaire_field_name(field.code, self.latest_form_model.id,
                                                                            parent_field_name)
                    fields_definition.append(get_field_definition_with_binary_type(field, field_name=es_field_name))
                continue
            fields_definition.append(
                get_field_definition(field,
                                     field_name=es_questionnaire_field_name(field.code, self.latest_form_model.id,
                                                                            parent_field_name)))

    def recreate_elastic_store(self):
        try:
            self.es.send_request('DELETE', [self.dbm.database_name, self.latest_form_model.id, '_mapping'])
        except ElasticHttpNotFoundError as e:
            pass
        self.es.put_mapping(self.dbm.database_name, self.latest_form_model.id, self.get_mappings())

    def recreate_and_populate_elastic_store(self):
        self.recreate_elastic_store()
        from datawinners.search.submission_index_task import async_populate_submission_index

        async_populate_submission_index.delay(self.dbm.database_name, self.latest_form_model.id)

    # def _add_text_field_mapping_for_submission(self, mapping_fields, field_def):
    #     name = field_def["name"]
    #     mapping_fields.update(
    #         {name: {"type": "multi_field", "fields": {
    #             name: {"type": "string"},
    #             name + "_value": {"type": "string", "index_analyzer": "sort_analyzer", "include_in_all": False},
    #             name + "_exact": {"type": "string", "index": "not_analyzed", "include_in_all": False},
    #         }}})

    def get_fields_mapping_by_field_def(self, doc_type, fields_definition):
        """
        fields_definition   = [{"name":form_model_id_q1, "type":"date", "date_format":"MM-yyyy"},{"name":form_model_id_q1, "type":"string"}]
        """
        mapping_fields = {}
        mapping = {"date_detection": False, "properties": mapping_fields}
        methods_dict = {"date": _add_date_field_mapping, "binary": _add_binary_field_mapping}
        
        for field_def in fields_definition:
            method = methods_dict.get(field_def.get("type"), _add_text_field_mapping)
            method(mapping_fields, field_def)

        ds_mapping = self._add_data_sender_details_to_mapping()
        all_id_fields = [field for field in self.latest_form_model.fields if
                         isinstance(field, UniqueIdField)]
        id_field_mapping = self._add_id_field_details_to_mapping(self.latest_form_model.id, all_id_fields)
        mapping_fields.update(ds_mapping)
        if bool(id_field_mapping):
            mapping_fields.update(id_field_mapping)
        return {doc_type: mapping}

    def _verify_unique_id_change(self):
        if self.old_form_model:
            old_unique_id_types = [(field.code, field.unique_id_type) for field in self.old_form_model.fields if
                                   isinstance(field, UniqueIdField)]
            new_unique_id_types = [(field.code, field.unique_id_type) for field in self.latest_form_model.fields if
                                   isinstance(field, UniqueIdField)]
            old_unique_id_types.sort()
            new_unique_id_types.sort()

            if old_unique_id_types != new_unique_id_types:
                raise FieldTypeChangeException()

    def _add_id_field_details_to_mapping(self, questionnaire_id, all_id_fields):
        id_field_mapping = {}
        for id_field in all_id_fields:
            key = es_unique_id_details_field_name(questionnaire_id + '_' + id_field.code)
            unique_field_mapping = {}
            entity_type = get_form_model_by_entity_type(self.dbm, [id_field.unique_id_type])
            if entity_type is not None and not isinstance(entity_type, NoneType):
                for field in entity_type.fields:
                    if field.type is "date":
                        unique_field_mapping.update({field.code: {'type': "date"}})
                    elif field.type is "double":
                        unique_field_mapping.update({field.code: {'type': "double"}})
                    else:
                        unique_field_mapping.update({field.code: {'type': "string", 'index_analyzer': 'sort_analyzer'}})
                id_field_mapping.update({key: {'properties': unique_field_mapping}})

        return id_field_mapping

    def _add_data_sender_details_to_mapping(self):
        return {"datasender": {
            "properties": {
                "email": {
                    "type": "string", 'index_analyzer': 'sort_analyzer'
                },
                "geo_code": {
                    "type": "double"
                },
                "id": {
                    "type": "string", 'index_analyzer': 'sort_analyzer'
                },
                "mobile_number": {
                    "type": "string", 'index_analyzer': 'sort_analyzer'
                },
                "name": {
                    "type": "string", 'index_analyzer': 'sort_analyzer'
                }
            }
        }}


class FieldTypeChangeException(Exception):
    def __str__(self):
        return self.message


def get_submission_meta_fields():
    return submission_meta_fields


def update_submission_search_for_datasender_edition(dbm, short_code, datasender_dict):
    kwargs = {"%s%s" % (SubmissionIndexConstants.DATASENDER_ID_KEY, "_value"): short_code}
    name = datasender_dict['name'] if datasender_dict['name'] else datasender_dict['mobile_number']
    fields_mapping = {SubmissionIndexConstants.DATASENDER_NAME_KEY: name, 'datasender': datasender_dict}
    project_form_model_ids = [project.id for project in get_all_projects(dbm, short_code)]
    chunk, i = ES_NUMBER_OF_TYPES_SUPPORTED, 0
    while i <= len(project_form_model_ids) / chunk:
        process_by_chunk_questionnaire(dbm, project_form_model_ids[i*chunk: (i+1) * chunk - 1], fields_mapping, kwargs)
        i += 1

def process_by_chunk_questionnaire(dbm, project_form_model_ids, fields_mapping, kwargs):
    assert len(project_form_model_ids) < ES_NUMBER_OF_TYPES_SUPPORTED
    query = elasticutils.S().es(urls=ELASTIC_SEARCH_URL, timeout=ELASTIC_SEARCH_TIMEOUT).indexes(
        dbm.database_name).doctypes(*project_form_model_ids)
    query = query[:query.count()].filter(**kwargs)

    for survey_response in query.values_dict('void'):
        SubmissionIndexUpdateHandler(dbm.database_name, survey_response._type).update_field_in_submission_index(
            survey_response._id, fields_mapping)


def _get_submissions_for_unique_id_entry(args, dbm, project):
    query = elasticutils.S().es(urls=ELASTIC_SEARCH_URL, timeout=ELASTIC_SEARCH_TIMEOUT).indexes(
        dbm.database_name).doctypes(project.id)
    query = query[:query.count()].filter(**args)
    return query


def update_submission_search_for_subject_edition(dbm, unique_id_type, subject_details):
    projects = []
    for row in dbm.load_all_rows_in_view('projects_by_subject_type', key=unique_id_type[0], include_docs=True):
        projects.append(Project.new_from_doc(dbm, ProjectDocument.wrap(row['doc'])))
    for project in projects:
        entity_field_code = None
        for field in project.entity_questions:
            if [field.unique_id_type] == unique_id_type:
                entity_field_code = field.code

        if entity_field_code:
            unique_id_field_name = es_questionnaire_field_name(entity_field_code, project.id)

            fields_mapping = {unique_id_field_name: subject_details.get('q2'),
                              unique_id_field_name + '_details': subject_details}
            args = {es_unique_id_code_field_name(unique_id_field_name): subject_details.get('q6')}

            query = _get_submissions_for_unique_id_entry(args, dbm, project)

            for survey_response in query.values_dict('void'):
                SubmissionIndexUpdateHandler(dbm.database_name, project.id).update_field_in_submission_index(
                    survey_response._id, fields_mapping)


def update_submission_search_index(submission_doc, dbm, refresh_index=True, form_model=None, bulk=False):
    es = get_elasticsearch_handle()
    if form_model is None:
        form_model = FormModel.get(dbm, submission_doc.form_model_id)
    search_dict = _meta_fields(submission_doc, dbm)
    _update_with_form_model_fields(dbm, submission_doc, search_dict, form_model)
    if bulk:
        return es.index_op(search_dict, doc_type=form_model.id, index=dbm.database_name, id=submission_doc.id)
    es.index(dbm.database_name, form_model.id, search_dict, id=submission_doc.id, refresh=refresh_index)


def status_message(status):
    return "Success" if status else "Error"


# TODO manage_index
def get_datasender_info(dbm, submission_doc):
    datasender_dict = {}
    if submission_doc.owner_uid:
        datasender_dict = _lookup_contact_by_uid(dbm, submission_doc.owner_uid)
    else:
        datasender_dict['name'] = submission_doc.created_by
        datasender_dict['id'] = UNKNOWN
        datasender_dict['location'] = []
        datasender_dict['email'] = UNKNOWN
        datasender_dict['geo_code'] = []
        datasender_dict['mobile_number'] = submission_doc.created_by

    return datasender_dict


def _meta_fields(submission_doc, dbm):
    search_dict = {}
    datasender_dict = get_datasender_info(dbm, submission_doc)
    search_dict.update({"status": status_message(submission_doc.status)})
    search_dict.update({"date": format_datetime(submission_doc.submitted_on, "MMM. dd, yyyy, hh:mm a", locale="en")})
    search_dict.update({"ds_id": datasender_dict.get('id', '')})
    search_dict.update({"ds_name": datasender_dict.get('name', '')})
    search_dict.update({"datasender": datasender_dict})
    search_dict.update({"error_msg": submission_doc.error_message})
    return search_dict


def _lookup_contact_by_uid(dbm, uid):
    ds_dict = {}
    try:
        if uid:
            contact = Contact.get(dbm, uid)
            mobile_number = contact.value('mobile_number')
            name = contact.value('name')
            ds_dict['mobile_number'] = mobile_number
            ds_dict['name'] = name if name else mobile_number
            ds_dict['email'] = contact.value('email') if contact.value('email') else UNKNOWN
            ds_dict['location'] = contact.value('location') if contact.value('location') else []
            ds_dict['geo_code'] = contact.geometry.get('coordinates') if contact.geometry.get('coordinates') else []
            ds_dict['id'] = contact.short_code
    except Exception:
        pass
    return ds_dict




# TODO:This is required only for the migration for creating submission indexes.To be removed following release10
def _get_select_field_by_revision(field, form_model, submission_doc):
    field_by_revision = form_model.get_field_by_code_and_rev(field.code, submission_doc.form_model_revision)
    return field_by_revision if field_by_revision else field


def _get_options_map(original_field):
    options_map = {}
    for option in original_field.options:
        options_map.update({option['val']: option['text']})
    return options_map


def _get_select_field_answer_from_snapshot(entry, field_for_revision):
    options = field_for_revision.get_options_map()
    value_list = []
    for answer_value in list(entry):
        value_list.append(options[answer_value])
    return ",".join(value_list)


def _fetch_single_select_answer(choices, field):
    if choices:
        choice_text = field.get_value_by_option(choices, default=choices)
    else:
        choice_text = ""

    return choice_text


def _fetch_multi_select_answer(choices, field):
    if choices:
        choice_text = [field.get_value_by_option(option, default=option) for option in choices.split(' ')]
    else:
        choice_text = []

    return choice_text


def _update_choice_value(entry, field):
    choices = entry.get(field.code)
    if field.is_single_select:
        entry[field.code] = _fetch_single_select_answer(choices, field)
    else:
        entry[field.code] = _fetch_multi_select_answer(choices, field)


def group_has_answers(group_answers, group_field):
    if not group_answers:
        return
    return filter(lambda field: group_answers[0].get(field.code), group_field.fields)


def _update_repeat_fields_with_choice_values(repeat_entries, repeat_field):
    for entry in repeat_entries:
        for field in repeat_field.fields:
            if field.is_field_set and field.is_group():
                group_answers = entry.get(field.code)
                if group_has_answers(group_answers, field):
                    _update_repeat_fields_with_choice_values(group_answers, field)
                else:
                    entry[field.code] = ''
            elif isinstance(field, SelectField):
                _update_choice_value(entry, field)


def _update_search_dict(dbm, form_model, fields, search_dict, submission_doc, submission_values, parent_field_name=None):
    for field in fields:
        entry = submission_values.get(field.code)
        label_to_be_displayed = get_label_to_be_displayed(entry, field, form_model, submission_doc)
        es_field_name = es_questionnaire_field_name(field.code, form_model.id, parent_field_name)

        if label_to_be_displayed:
            if 'media' not in search_dict.keys():
                search_dict.update({'media': {}})

            if isinstance(field, PhotoField):
                search_dict['media'].update({es_field_name:
                    {
                        'type': 'image',
                        'value': entry,
                        'download_link': '/download/attachment/' + submission_doc.id + '/' + entry,
                        'preview_link': '/download/attachment/' + submission_doc.id + '/preview_' + entry,
                    }
                })

            if isinstance(field, AudioField):
                search_dict['media'].update({es_field_name:
                    {
                        'type': 'audio',
                        'value': entry,
                        'download_link': '/download/attachment/' + submission_doc.id + '/' + entry,
                    }
                })

            if isinstance(field, VideoField):
                search_dict['media'].update({es_field_name:
                    {
                        'type': 'video',
                        'value': entry,
                        'download_link': '/download/attachment/' + submission_doc.id + '/' + entry,
                    }
                })

            if isinstance(field, FieldSet):
                if field.is_group():
                    for value in entry:
                        _update_search_dict(dbm, form_model, field.fields, search_dict, submission_doc, value, field.code)
                else:
                    _update_repeat_fields_with_choice_values(label_to_be_displayed, field)
                    _update_name_unique_code(dbm, label_to_be_displayed, field)
                    search_dict.update({es_field_name: json.dumps(label_to_be_displayed)})
            elif field.is_entity_field:
                entity, choice_to_entity_entry = get_entity(dbm, entry, field, form_model, submission_doc)
                if entry:
                    search_dict.update({es_unique_id_details_field_name(es_field_name): entity})
                    search_dict.update({es_unique_id_code_field_name(es_field_name): choice_to_entity_entry or UNKNOWN})
                search_dict.update({es_field_name: entry and entity.get('q2')})
            else:
                search_dict.update({es_field_name: label_to_be_displayed})

    search_dict.update({'void': submission_doc.void})
    search_dict.update({'is_anonymous': submission_doc.is_anonymous_submission})


def get_label_to_be_displayed(entry, field, form_model, submission_doc):
    if field.type == "select":
        old_field = _get_select_field_by_revision(field, form_model, submission_doc)
        if old_field.type == "select":
            entry = old_field.get_option_value_list(entry)
        elif old_field.type == "select1":
            entry = ",".join(old_field.get_option_value_list(entry))
    elif field.type == "select_one_external":
        old_field = _get_select_field_by_revision(field, form_model, submission_doc)
        if isinstance(old_field, SelectOneExternalField):
            itemsets_data = form_model.get_attachments('itemsets.csv')
            entry = old_field.get_option_value_list(entry, itemsets_data)
    elif field.type == "select1":
        old_field = _get_select_field_by_revision(field, form_model, submission_doc)
        if old_field.type == "select":
            entry = old_field.get_option_value_list(entry)
        elif old_field.type == "select1":
            entry = ",".join(old_field.get_option_value_list(entry))
    elif field.type == 'text':
        field_for_revision = form_model.get_field_by_code_and_rev(field.code, submission_doc.form_model_revision)
        if isinstance(field_for_revision, SelectField):
            entry = _get_select_field_answer_from_snapshot(entry, field_for_revision)
    elif field.type == "date":
        try:
            if form_model.revision != submission_doc.form_model_revision:
                old_submission_value = entry
                to_format = field.date_format
                field_for_revision = form_model.get_field_by_code_and_rev(field.code,
                                                                          submission_doc.form_model_revision)
                if isinstance(field_for_revision, DateField):
                    current_date = field_for_revision.__date__(entry)
                    entry = current_date.strftime(DateField.DATE_DICTIONARY.get(to_format))
                elif isinstance(field_for_revision, SelectField):
                    entry = _get_select_field_answer_from_snapshot(entry, field_for_revision)
                logger.info("Converting old date submission from %s to %s" % (old_submission_value, entry))
        except Exception:
            pass
    return entry


def get_entity(dbm, entry, field, form_model, submission_doc):
    choice_to_entity_entry = entry
    original_field = form_model.get_field_by_code_and_rev(field.code, submission_doc.form_model_revision)
    if is_original_question_changed_from_choice_answer_type(original_field, field):
        choice_to_entity_entry = convert_choice_options_to_options_text(original_field, entry)
    return lookup_entity(dbm, choice_to_entity_entry, [field.unique_id_type]), choice_to_entity_entry


def _update_name_unique_code(dbm, repeat_entries, fieldset_field):
    for entry in repeat_entries:
        for field in fieldset_field.fields:
            if isinstance(field, UniqueIdField):
                unique_code = entry.get(field.code)
                unique_id_name = lookup_entity(dbm, str(unique_code), [field.unique_id_type]).get('q2')
                entry[field.code + '_unique_code'] = unique_code if unique_code else ''
                entry[field.code] = unique_id_name
            elif isinstance(field, FieldSet):
                _update_name_unique_code(dbm, entry.get(field.code), field)


def _update_with_form_model_fields(dbm, submission_doc, search_dict, form_model):
    # Submission value may have capitalized keys in some cases. This conversion is to do
    # case insensitive lookup.
    submission_values = OrderedDict((k, v) for k, v in submission_doc.values.iteritems())
    _update_search_dict(dbm, form_model, form_model.fields, search_dict, submission_doc, submission_values)
    return search_dict


def get_unregistered_datasenders(dbm, questionnaire_id):
    facets = elasticutils.S().es(urls=ELASTIC_SEARCH_URL, timeout=ELASTIC_SEARCH_TIMEOUT).indexes(dbm.database_name) \
        .doctypes(questionnaire_id).filter(is_anonymous=True, ds_id='n/a', void=False) \
        .facet('ds_name_exact', filtered=True).facet_counts()['ds_name_exact']

    return [facet['term'] for facet in facets]


def get_unregistered_datasenders_count(dbm, questionnaire_id):
    return len(get_unregistered_datasenders(dbm, questionnaire_id))


def get_non_deleted_submission_count(dbm, questionnaire_id):
    return elasticutils.S().es(urls=ELASTIC_SEARCH_URL, timeout=ELASTIC_SEARCH_TIMEOUT) \
        .indexes(dbm.database_name).doctypes(questionnaire_id) \
        .filter(void=False).count()
