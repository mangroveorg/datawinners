import logging
from string import lower

from babel.dates import format_datetime
from pyelasticsearch.exceptions import ElasticHttpError, ElasticHttpNotFoundError

from mangrove.form_model.field import DateField
from datawinners.project.models import get_all_projects
from datawinners.search.submission_index_constants import SubmissionIndexConstants
from datawinners.search.submission_index_helper import SubmissionIndexUpdateHandler
from mangrove.errors.MangroveException import DataObjectNotFound
from datawinners.search.index_utils import get_elasticsearch_handle, get_fields_mapping_by_field_def, get_field_definition
from mangrove.datastore.entity import get_by_short_code_include_voided, Entity
from mangrove.form_model.form_model import get_form_model_by_code, FormModel


logger = logging.getLogger("datawinners")

ES_SUBMISSION_FIELD_DS_ID = "ds_id"
ES_SUBMISSION_FIELD_DS_NAME = "ds_name"
ES_SUBMISSION_FIELD_DS_NAME = "ds_name"
ES_SUBMISSION_FIELD_DATE = "date"
ES_SUBMISSION_FIELD_STATUS = "status"
ES_SUBMISSION_FIELD_ERROR_MSG = "error_msg"
ES_SUBMISSION_FIELD_ENTITY_SHORT_CODE = "entity_short_code"

meta_fields = [ES_SUBMISSION_FIELD_DS_ID, ES_SUBMISSION_FIELD_DS_NAME, ES_SUBMISSION_FIELD_DATE,
               ES_SUBMISSION_FIELD_STATUS, ES_SUBMISSION_FIELD_ERROR_MSG, ES_SUBMISSION_FIELD_ENTITY_SHORT_CODE]

submission_meta_fields = [{"name": ES_SUBMISSION_FIELD_DATE, "type": "date", "date_format": 'submission_date_format'},
                          {"name": ES_SUBMISSION_FIELD_STATUS},
                          {"name": ES_SUBMISSION_FIELD_DS_NAME},
                          {"name": ES_SUBMISSION_FIELD_DS_ID},
                          {"name": ES_SUBMISSION_FIELD_ERROR_MSG},
                          {"name": ES_SUBMISSION_FIELD_ENTITY_SHORT_CODE}]

submission_meta_field_names = dict([(field["name"], None) for field in submission_meta_fields])


def is_submission_meta_field(field_name):
    return submission_meta_field_names.has_key(field_name)


def es_field_name(field_code, form_model_id):
    """
        prefixes form_model id to namespace all additional fields on questionnaire (ds_name, ds_id, status and date are not prefixed)
    :param field_code:
    """
    return field_code if is_submission_meta_field(field_code) else "%s_%s" % (form_model_id, lower(field_code))


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
            [k + f["fields"][k + "_value"]["type"] for k, f in mapping_old.values()[0]['properties'].items()])

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
        mapping = get_fields_mapping_by_field_def(doc_type=self.form_model.id, fields_definition=fields_definition)
        return mapping

    def recreate_elastic_store(self):
        self.es.send_request('DELETE', [self.dbm.database_name, self.form_model.id, '_mapping'])
        self.es.put_mapping(self.dbm.database_name, self.form_model.id, self.get_mappings())
        from datawinners.search.submission_index_task import async_populate_submission_index
        async_populate_submission_index.delay(self.dbm.database_name, self.form_model.form_code)



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
    project_form_model_ids = [project.value['qid'] for project in get_all_projects(dbm)]

    filtered_query = SubmissionQueryBuilder().query_all(dbm.database_name, *project_form_model_ids, **kwargs)

    for survey_response in filtered_query.all():
        SubmissionIndexUpdateHandler(dbm.database_name, survey_response._type).update_field_in_submission_index(
            survey_response._id, fields_mapping)


def _get_form_models_from_projects(dbm, projects):
    form_models = []
    for project in projects:
        form_models.append(FormModel.get(dbm, project.doc['qid']))
    return form_models


def update_submission_search_for_subject_edition(entity_doc, dbm):
    from datawinners.search.submission_query import SubmissionQueryBuilder

    entity_type = entity_doc.entity_type
    projects = dbm.load_all_rows_in_view('projects_by_subject_type', key=entity_type[0], include_docs=True)
    form_models = _get_form_models_from_projects(dbm, projects)

    for form_model in form_models:
        entity_field_name = lower(form_model.entity_question.code)
        fields_mapping = {es_field_name(entity_field_name, form_model.id): entity_doc.data['name']['value']}
        args = {'entity_short_code': entity_doc.short_code}
        survey_response_filtered_query = SubmissionQueryBuilder(form_model).query_all(dbm.database_name, form_model.id,
                                                                                      **args)

        for survey_response in survey_response_filtered_query.all():
            SubmissionIndexUpdateHandler(dbm.database_name, form_model.id).update_field_in_submission_index(
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
    return uid or "NA", "NA"


def lookup_entity_name(dbm, id, entity_type):
    try:
        if id:
            return get_by_short_code_include_voided(dbm, id, entity_type).value("name")
    except DataObjectNotFound:
        pass
    return id or "NA"


def _update_with_form_model_fields(dbm, submission_doc, search_dict, form_model):
    for field in form_model.fields:
        entry = submission_doc.values.get(lower(field.code))
        if field.is_entity_field:
            search_dict.update({"entity_short_code": entry or 'NA'})
            entry = lookup_entity_name(dbm, entry, form_model.entity_type)
        elif field.type == "select":
            entry = field.get_option_value_list(entry)
        elif field.type == "select1":
            entry = ",".join(field.get_option_value_list(entry))
        elif field.type == "date":
            try:
                if form_model.revision != submission_doc.form_model_revision:
                    old_submission_value = entry
                    to_format = field.date_format
                    current_format = form_model.get_field_by_code_and_rev(field.code, submission_doc.form_model_revision).__date__(entry)
                    entry = current_format.strftime(DateField.DATE_DICTIONARY.get(to_format))
                    logger.info("Converting old date submission from %s to %s" % (old_submission_value, entry))
            except Exception as ignore_conversion_errors:
                pass

        search_dict.update({es_field_name(lower(field.code), form_model.id): entry})

    search_dict.update({'void': submission_doc.void})
    return search_dict
