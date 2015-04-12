from datawinners.entity.import_data import load_all_entities_of_type
from datawinners.search.all_datasender_search import get_all_data_sender_mobile_numbers
from datawinners.search.submission_index import get_unregistered_datasenders


def get_data_sender_phone_numbers(dbm, questionnaire, form):
    selected_recepients = form.cleaned_data['to']
    if selected_recepients == "All":
        return get_all_data_sender_mobile_numbers(dbm)
    elif selected_recepients == "Associated":
        return _get_registered_data_senders(dbm, questionnaire)
    elif selected_recepients == "AllSubmitted":
        return _get_registered_data_senders(dbm,questionnaire) + get_unregistered_datasenders(dbm, questionnaire.id)
    return []


def _get_registered_data_senders(dbm, questionnaire):
    return [data_sender_doc['mobile_number'] for data_sender_doc in questionnaire.get_data_senders(dbm)]
