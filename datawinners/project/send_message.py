from datawinners.entity.import_data import load_all_entities_of_type
from datawinners.search.submission_index import get_unregistered_datasenders


def get_data_sender_phone_numbers(dbm, questionnaire, form):
    selected_recepients = form.cleaned_data['to']
    if selected_recepients == "All":
        data_sender_docs = _get_all_data_senders(dbm)
        return [data_sender_doc['mobile_number'] for data_sender_doc in data_sender_docs]
    elif selected_recepients == "Associated":
        return _get_registered_data_senders(dbm, questionnaire)
    elif selected_recepients == "AllSubmitted":
        return _get_registered_data_senders(dbm,questionnaire) + get_unregistered_datasenders(dbm, questionnaire.id)
    return []

def _get_all_data_senders(dbm):
    data_senders, fields, labels = load_all_entities_of_type(dbm)
    return [dict(zip(fields, data["cols"])) for data in data_senders]

def _get_registered_data_senders(dbm, questionnaire):
    return [data_sender_doc['mobile_number'] for data_sender_doc in questionnaire.get_data_senders(dbm)]
