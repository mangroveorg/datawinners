import json
import logging
from collections import OrderedDict
from string import lower

from babel.dates import format_datetime
import elasticutils
from pyelasticsearch.exceptions import ElasticHttpError, ElasticHttpNotFoundError

from datawinners.project.views.utils import is_original_question_changed_from_choice_answer_type, \
    convert_choice_options_to_options_text
from datawinners.settings import ELASTIC_SEARCH_URL, ELASTIC_SEARCH_TIMEOUT
from mangrove.datastore.documents import ProjectDocument
from datawinners.search.submission_index_meta_fields import submission_meta_fields
from mangrove.form_model.field import DateField, UniqueIdField, SelectField, FieldSet
from datawinners.project.models import get_all_projects
from datawinners.search.submission_index_constants import SubmissionIndexConstants
from datawinners.search.submission_index_helper import SubmissionIndexUpdateHandler
from mangrove.errors.MangroveException import DataObjectNotFound
from datawinners.search.index_utils import get_elasticsearch_handle, get_field_definition, _add_date_field_mapping, \
    es_unique_id_code_field_name, \
    es_questionnaire_field_name
from mangrove.datastore.entity import get_by_short_code_include_voided, Entity
from mangrove.form_model.form_model import FormModel
from mangrove.form_model.project import Project


logger = logging.getLogger("datawinners")
UNKNOWN = "N/A"


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

    def _has_fields_changed(self, mapping, mapping_old):
        new_fields_with_format = set(
            [k + f["fields"][k + "_value"]["type"] for k, f in mapping.values()[0]['properties'].items()])
        old_fields_with_format = set(
            [k + f["fields"][k + "_value"]["type"] for k, f in mapping_old.values()[0]['properties'].items() if
             f.get("fields")])

        return new_fields_with_format != old_fields_with_format

    def _verify_change_involving_date_field(self, mapping, mapping_old):
        old_q_codes = mapping_old.values()[0]['properties'].keys()
        new_q_code = mapping.values()[0]['properties'].keys()
        new_date_fields_with_format = set(
            [k + f["fields"][k + "_value"]["format"] for k, f in mapping.values()[0]['properties'].items()
             if f["fields"][k + "_value"]["type"] == "date" and k in old_q_codes])
        old_date_fields_with_format = set(
            [k + f["fields"][k + "_value"]["format"] for k, f in mapping_old.values()[0]['properties'].items()
             if f.get('fields') and f["fields"][k + "_value"]["type"] == "date" and k in new_q_code])
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
                unique_id_field_name = es_questionnaire_field_name(field.code, self.latest_form_model.id)
                fields_definition.append(
                    get_field_definition(field, field_name=es_unique_id_code_field_name(unique_id_field_name)))

            if isinstance(field, FieldSet) and field.is_group():
                self._get_submission_fields(fields_definition, field.fields, field.code)
                continue
            fields_definition.append(
                get_field_definition(field,
                                     field_name=es_questionnaire_field_name(field.code, self.latest_form_model.id,
                                                                            parent_field_name)))

    def recreate_elastic_store(self):
        self.es.send_request('DELETE', [self.dbm.database_name, self.latest_form_model.id, '_mapping'])
        self.es.put_mapping(self.dbm.database_name, self.latest_form_model.id, self.get_mappings())

    def recreate_and_populate_elastic_store(self):
        self.recreate_elastic_store()
        from datawinners.search.submission_index_task import async_populate_submission_index

        async_populate_submission_index.delay(self.dbm.database_name, self.latest_form_model.id)

    def _add_text_field_mapping_for_submission(self, mapping_fields, field_def):
        name = field_def["name"]
        mapping_fields.update(
            {name: {"type": "multi_field", "fields": {
                name: {"type": "string"},
                name + "_value": {"type": "string", "index_analyzer": "sort_analyzer", "include_in_all": False},
                name + "_exact": {"type": "string", "index": "not_analyzed", "include_in_all": False},
            }}})

    def get_fields_mapping_by_field_def(self, doc_type, fields_definition):
        """
        fields_definition   = [{"name":form_model_id_q1, "type":"date", "date_format":"MM-yyyy"},{"name":form_model_id_q1, "type":"string"}]
        """
        mapping_fields = {}
        mapping = {"date_detection": False, "properties": mapping_fields}
        for field_def in fields_definition:
            if field_def.get("type") is "date":
                _add_date_field_mapping(mapping_fields, field_def)
            else:
                self._add_text_field_mapping_for_submission(mapping_fields, field_def)
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


class FieldTypeChangeException(Exception):
    def __str__(self):
        return self.message


def get_submission_meta_fields():
    return submission_meta_fields


def update_submission_search_for_datasender_edition(dbm, short_code, ds_name):
    from datawinners.search.submission_query import SubmissionQueryBuilder

    kwargs = {"%s%s" % (SubmissionIndexConstants.DATASENDER_ID_KEY, "_value"): short_code}
    fields_mapping = {SubmissionIndexConstants.DATASENDER_NAME_KEY: ds_name}
    project_form_model_ids = [project.id for project in get_all_projects(dbm, short_code)]

    filtered_query = SubmissionQueryBuilder().query_all(dbm.database_name, *project_form_model_ids, **kwargs)

    for survey_response in filtered_query.all():
        SubmissionIndexUpdateHandler(dbm.database_name, survey_response._type).update_field_in_submission_index(
            survey_response._id, fields_mapping)


def update_submission_search_for_subject_edition(dbm, unique_id_type, short_code, last_name):
    from datawinners.search.submission_query import SubmissionQueryBuilder

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

            fields_mapping = {unique_id_field_name: last_name}
            args = {es_unique_id_code_field_name(unique_id_field_name): short_code}

            survey_response_filtered_query = SubmissionQueryBuilder(project).query_all(dbm.database_name, project.id,
                                                                                       **args)

            for survey_response in survey_response_filtered_query.all():
                SubmissionIndexUpdateHandler(dbm.database_name, project.id).update_field_in_submission_index(
                    survey_response._id, fields_mapping)


def update_submission_search_index(submission_doc, dbm, refresh_index=True):
    es = get_elasticsearch_handle()
    form_model = FormModel.get(dbm, submission_doc.form_model_id)
    search_dict = _meta_fields(submission_doc, dbm)
    _update_with_form_model_fields(dbm, submission_doc, search_dict, form_model)
    es.index(dbm.database_name, form_model.id, search_dict, id=submission_doc.id, refresh=refresh_index)


def status_message(status):
    return "Success" if status else "Error"


# TODO manage_index
def _get_datasender_info(dbm, submission_doc):
    if submission_doc.owner_uid:
        datasender_name, datasender_id = lookup_entity_by_uid(dbm, submission_doc.owner_uid)
    else:
        datasender_name, datasender_id = submission_doc.created_by, UNKNOWN
    return datasender_id, datasender_name


def _meta_fields(submission_doc, dbm):
    search_dict = {}
    datasender_id, datasender_name = _get_datasender_info(dbm, submission_doc)
    search_dict.update({"status": status_message(submission_doc.status)})
    search_dict.update({"date": format_datetime(submission_doc.submitted_on, "MMM. dd, yyyy, hh:mm a", locale="en")})
    search_dict.update({"ds_id": datasender_id})
    search_dict.update({"ds_name": datasender_name})
    search_dict.update({"error_msg": submission_doc.error_message})
    return search_dict


def lookup_entity_by_uid(dbm, uid):
    try:
        if uid:
            entity = Entity.get(dbm, uid)
            return entity.value('name'), entity.short_code
    except Exception:
        pass
    return UNKNOWN, UNKNOWN


def lookup_entity_name(dbm, id, entity_type):
    try:
        if id:
            return get_by_short_code_include_voided(dbm, id, entity_type).value("name")
    except DataObjectNotFound:
        pass
    return " "


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
        choice_text = field.get_value_by_option(choices)
    else:
        choice_text = ""

    return choice_text


def _fetch_multi_select_answer(choices, field):
    if choices:
        choice_text = [field.get_value_by_option(option) for option in choices.split(' ')]
    else:
        choice_text = []

    return choice_text


def _update_choice_value(entry, field):
    choices = entry.get(field.code)
    if field.is_single_select:
        entry[field.code] = _fetch_single_select_answer(choices, field)
    else:
        entry[field.code] = _fetch_multi_select_answer(choices, field)


def _update_repeat_fields_with_choice_values(repeat_entries, repeat_field):
    for entry in repeat_entries:
        for field in repeat_field.fields:
            if field.is_field_set and field.is_group():
                _update_repeat_fields_with_choice_values(entry.get(field.code), field)
            elif isinstance(field, SelectField):
                _update_choice_value(entry, field)


def _update_search_dict(dbm, form_model, fields, search_dict, submission_doc, submission_values,
                        parent_field_name=None):
    for field in fields:
        field_code = field.code
        entry = submission_values.get(field_code)
        if field.is_entity_field:
            if entry:
                original_field = form_model.get_field_by_code_and_rev(field.code, submission_doc.form_model_revision)

                if is_original_question_changed_from_choice_answer_type(original_field, field):
                    entry = convert_choice_options_to_options_text(original_field, entry)
                entity_name = lookup_entity_name(dbm, entry, [field.unique_id_type])
                entry_code = entry
                search_dict.update(
                    {es_unique_id_code_field_name(
                        es_questionnaire_field_name(field.code, form_model.id)): entry_code or UNKNOWN})
                entry = entity_name
        elif field.type == "select":
            field = _get_select_field_by_revision(field, form_model, submission_doc)
            if field.type == "select":
                entry = field.get_option_value_list(entry)
            elif field.type == "select1":
                entry = ",".join(field.get_option_value_list(entry))
        elif field.type == "select1":
            field = _get_select_field_by_revision(field, form_model, submission_doc)
            if field.type == "select":
                entry = field.get_option_value_list(entry)
            elif field.type == "select1":
                entry = ",".join(field.get_option_value_list(entry))
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
            except Exception as ignore_conversion_errors:
                pass
        if entry:
            if isinstance(field, FieldSet):
                if field.is_group():
                    for value in submission_values[field_code]:
                        _update_search_dict(dbm, form_model, field.fields, search_dict, submission_doc, value,
                                            field.code)
                else:
                    _update_repeat_fields_with_choice_values(entry, field)
                    search_dict.update(
                        {es_questionnaire_field_name(field_code, form_model.id, parent_field_name): json.dumps(entry)})
            else:
                search_dict.update({es_questionnaire_field_name(field.code, form_model.id, parent_field_name): entry})

    search_dict.update({'void': submission_doc.void})
    search_dict.update({'is_anonymous': submission_doc.is_anonymous_submission})


def _update_with_form_model_fields(dbm, submission_doc, search_dict, form_model):
    # Submission value may have capitalized keys in some cases. This conversion is to do
    # case insensitive lookup.
    submission_values = OrderedDict((k, v) for k, v in submission_doc.values.iteritems())
    _update_search_dict(dbm, form_model, form_model.fields, search_dict, submission_doc, submission_values)
    return search_dict


def get_unregistered_datasenders(dbm, questionnaire_id):
    facets = elasticutils.S().es(urls=ELASTIC_SEARCH_URL, timeout=ELASTIC_SEARCH_TIMEOUT).indexes(dbm.database_name)\
            .doctypes(questionnaire_id).filter(is_anonymous=True, ds_id='n/a', void=False)\
            .facet('ds_name_exact', filtered=True).facet_counts()['ds_name_exact']

    return [facet['term'] for facet in facets]


def get_unregistered_datasenders_count(dbm, questionnaire_id):
    return len(get_unregistered_datasenders(dbm, questionnaire_id))


def get_non_deleted_submission_count(dbm, questionnaire_id):
    return elasticutils.S().es(urls=ELASTIC_SEARCH_URL, timeout=ELASTIC_SEARCH_TIMEOUT) \
        .indexes(dbm.database_name).doctypes(questionnaire_id) \
        .filter(void=False).count()
