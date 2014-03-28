import logging
from collections import OrderedDict
from string import lower

from babel.dates import format_datetime
from mangrove.datastore.documents import ProjectDocument
from pyelasticsearch.exceptions import ElasticHttpError, ElasticHttpNotFoundError
from datawinners.search.submission_index_meta_fields import submission_meta_fields

from mangrove.form_model.field import DateField
from datawinners.project.models import get_all_projects, Project
from datawinners.search.submission_index_constants import SubmissionIndexConstants
from datawinners.search.submission_index_helper import SubmissionIndexUpdateHandler
from mangrove.errors.MangroveException import DataObjectNotFound
from datawinners.search.index_utils import get_elasticsearch_handle, get_field_definition, es_field_name, _add_date_field_mapping, es_unique_id_code_field_name
from mangrove.datastore.entity import get_by_short_code_include_voided, Entity
from mangrove.form_model.form_model import get_form_model_by_code, FormModel


logger = logging.getLogger("datawinners")
UNKNOWN = "N/A"

def get_code_from_es_field_name(es_field_name, form_model_id):
    for item in es_field_name.split('_'):
        if item != 'value' and item != form_model_id:
            return item


def create_submission_mapping(dbm, form_model):
    es = get_elasticsearch_handle()
    SubmissionSearchStore(dbm, es, form_model).update_store()



class SubmissionSearchStore():
    def __init__(self, dbm, es, form_model):
        self.dbm = dbm
        self.es = es
        self.form_model = form_model

    def update_store(self):
        mapping = self.get_mappings()
        try:
            mapping_old = self.get_old_mappings()
            if mapping_old:
                self._verify_change_involving_date_field(mapping, mapping_old)
            if not mapping_old or self._has_fields_changed(mapping, mapping_old):
                self.es.put_mapping(self.dbm.database_name, self.form_model.id, mapping)

        except (ElasticHttpError, ChangeInvolvingDateFieldException) as e:
            if isinstance(e, ChangeInvolvingDateFieldException) or e[1].startswith('MergeMappingException'):
                self.recreate_elastic_store()
            else:
                logger.error(e)
        except Exception as e:
            logger.error(e)

    def _has_fields_changed(self, mapping, mapping_old):
        new_fields_with_format = set(
            [k + f["fields"][k + "_value"]["type"] for k, f in mapping.values()[0]['properties'].items()])
        old_fields_with_format = set(
            [k + f["fields"][k + "_value"]["type"] for k, f in mapping_old.values()[0]['properties'].items() if f.get("fields")])

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
            raise ChangeInvolvingDateFieldException()

    def get_old_mappings(self):
        mapping_old = []
        try:
            mapping_old = self.es.get_mapping(index=self.dbm.database_name, doc_type=self.form_model.id)
        except ElasticHttpNotFoundError as e:
            pass
        return mapping_old

    def get_mappings(self):
        fields_definition = []
        fields_definition.extend(get_submission_meta_fields())
        for field in self.form_model.fields:
            fields_definition.append(
                get_field_definition(field, field_name=es_field_name(field.code, self.form_model.id)))
        mapping = self.get_fields_mapping_by_field_def(doc_type=self.form_model.id, fields_definition=fields_definition)
        return mapping

    def recreate_elastic_store(self):
        self.es.send_request('DELETE', [self.dbm.database_name, self.form_model.id, '_mapping'])
        self.es.put_mapping(self.dbm.database_name, self.form_model.id, self.get_mappings())
        from datawinners.search.submission_index_task import async_populate_submission_index
        async_populate_submission_index.delay(self.dbm.database_name, self.form_model.form_code)

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


class ChangeInvolvingDateFieldException(Exception):
    def __str__(self):
        return self.message


def get_submission_meta_fields():
    return submission_meta_fields


def submission_update_on_entity_edition(entity_doc, dbm):
    if entity_doc.entity_type != ['reporter']:
        update_submission_search_for_subject_edition(entity_doc, dbm)
    else:
        update_submission_search_for_datasender_edition(entity_doc, dbm)


def update_submission_search_for_datasender_edition(entity_doc, dbm):
    from datawinners.search.submission_query import SubmissionQueryBuilder

    kwargs = {"%s%s"%(SubmissionIndexConstants.DATASENDER_ID_KEY, "_value"): entity_doc.short_code}
    fields_mapping = {SubmissionIndexConstants.DATASENDER_NAME_KEY: entity_doc.data['name']['value']}
    project_form_model_ids = [project.id for project in get_all_projects(dbm)]

    filtered_query = SubmissionQueryBuilder().query_all(dbm.database_name, *project_form_model_ids, **kwargs)

    for survey_response in filtered_query.all():
        SubmissionIndexUpdateHandler(dbm.database_name, survey_response._type).update_field_in_submission_index(
            survey_response._id, fields_mapping)


def update_submission_search_for_subject_edition(entity_doc, dbm):
    from datawinners.search.submission_query import SubmissionQueryBuilder

    entity_type = entity_doc.entity_type
    projects = []
    for row in dbm.load_all_rows_in_view('projects_by_subject_type', key=entity_type[0], include_docs=True):
            projects.append(Project.new_from_doc(dbm, ProjectDocument.wrap(row['doc'])))
    for project in projects:
        entity_field_code = None
        for field in project.entity_questions:
            if [field.unique_id_type] == entity_type:
                entity_field_code = field.code

        if entity_field_code:
            unique_id_field_name = es_field_name(entity_field_code, project.id)

            fields_mapping = {unique_id_field_name: entity_doc.data['name']['value']}
            args = {es_unique_id_code_field_name(unique_id_field_name): entity_doc.short_code}

            survey_response_filtered_query = SubmissionQueryBuilder(project).query_all(dbm.database_name, project.id,
                                                                                          **args)

            for survey_response in survey_response_filtered_query.all():
                SubmissionIndexUpdateHandler(dbm.database_name, project.id).update_field_in_submission_index(
                    survey_response._id, fields_mapping)


def update_submission_search_index(submission_doc, dbm, refresh_index=True):
    es = get_elasticsearch_handle()
    form_model = get_form_model_by_code(dbm, submission_doc.form_code)
    #submission_doc = SurveyResponseDocument.load(dbm.database, feed_submission_doc.id)
    search_dict = _meta_fields(submission_doc, dbm)
    _update_with_form_model_fields(dbm, submission_doc, search_dict, form_model)
    es.index(dbm.database_name, form_model.id, search_dict, id=submission_doc.id, refresh=refresh_index)


def status_message(status):
    return "Success" if status else "Error"


#TODO manage_index
def _meta_fields(submission_doc, dbm):
    search_dict = {}
    datasender_name, datasender_id = lookup_entity_by_uid(dbm, submission_doc.owner_uid)
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
    return UNKNOWN

#TODO:This is required only for the migration for creating submission indexes.To be removed following release10
def _update_select_field_by_revision(field, form_model, submission_doc):
    field_by_revision = form_model.get_field_by_code_and_rev(field.code, submission_doc.form_model_revision)
    return field_by_revision if field_by_revision else field


def _update_with_form_model_fields(dbm, submission_doc, search_dict, form_model):
    #Submission value may have capitalized keys in some cases. This conversion is to do
    #case insensitive lookup.
    submission_values = OrderedDict((k.lower(), v) for k,v in submission_doc.values.iteritems())
    for field in form_model.fields:
        entry = submission_values.get(lower(field.code))
        if field.is_entity_field:
            entity_name = lookup_entity_name(dbm, entry, [field.unique_id_type])
            entry_code = UNKNOWN if entity_name == UNKNOWN else entry
            search_dict.update({es_unique_id_code_field_name(es_field_name(lower(field.code), form_model.id)): entry_code or UNKNOWN})
            entry = entity_name
        elif field.type == "select":
            field = _update_select_field_by_revision(field, form_model, submission_doc)
            if field.type == "select":
                entry = field.get_option_value_list(entry)
            elif field.type == "select1":
                entry = ",".join(field.get_option_value_list(entry))
        elif field.type == "select1":
            field = _update_select_field_by_revision(field, form_model, submission_doc)
            if field.type == "select":
                entry = field.get_option_value_list(entry)
            elif field.type == "select1":
                entry = ",".join(field.get_option_value_list(entry))
        elif field.type == "date":
            try:
                if form_model.revision != submission_doc.form_model_revision:
                    old_submission_value = entry
                    to_format = field.date_format
                    current_date = form_model.get_field_by_code_and_rev(field.code, submission_doc.form_model_revision).__date__(entry)
                    entry = current_date.strftime(DateField.DATE_DICTIONARY.get(to_format))
                    logger.info("Converting old date submission from %s to %s" % (old_submission_value, entry))
            except Exception as ignore_conversion_errors:
                pass
        if entry:
            search_dict.update({es_field_name(lower(field.code), form_model.id): entry})

    search_dict.update({'void': submission_doc.void})
    return search_dict


