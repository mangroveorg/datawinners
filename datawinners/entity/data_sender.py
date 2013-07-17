from datawinners.entity.import_data import get_entity_type_fields, _tabulate_data
from mangrove.datastore.entity import _from_row_to_entity
from mangrove.form_model.form_model import get_form_model_by_code, REPORTER


def load_data_senders(manager, short_codes):
    form_model = get_form_model_by_code(manager, 'reg')
    fields, labels, codes = get_entity_type_fields(manager, REPORTER)
    keys = [([REPORTER], short_code) for short_code in short_codes]
    rows = manager.view.by_short_codes(reduce=False, include_docs=True, keys=keys)
    data = [_tabulate_data(_from_row_to_entity(manager, row), form_model, codes) for row in rows]
    return data, fields, labels