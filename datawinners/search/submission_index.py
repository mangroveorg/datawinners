import elasticutils
from datawinners.search.index_utils import get_fields_mapping
from datawinners.settings import ELASTIC_SEARCH_URL
from mangrove.datastore.datadict import DataDictType
from mangrove.form_model.field import TextField, DateField


def meta_data_mapping(form_model):
    return


def create_submission_mapping(dbm, form_model):
    es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
    fields = []
    fields.append(DateField("Submission Date", "date", "Submission Date", 'dd.mm.yyyy', DataDictType(dbm)))
    fields.append(TextField("Status", "status", "Status", DataDictType(dbm)))
    fields.append(TextField("Datasender Name","ds_name","Datasender Name",DataDictType(dbm)))
    fields.append(TextField("Datasender Id","ds_id","Datasender Id",DataDictType(dbm)))
    fields.extend(form_model.fields)
    mapping = get_fields_mapping(form_model.id, fields, 'code')
    #mapping = merge_mapping(mapping, meta_data_mapping(form_model))
    es.put_mapping(dbm.database_name, form_model.id, mapping)


#es = elasticutils.get_es(urls=ELASTIC_SEARCH_URL)
#es.delete_all_indexes()