from collections import OrderedDict
from mangrove.datastore.documents import FormModelDocument
from mangrove.form_model.form_model import FormModel, get_form_model_by_entity_type


def get_all_projects_for_datasender(dbm, data_sender_id):
    rows = dbm.load_all_rows_in_view('projects_by_datasenders', key=data_sender_id, include_docs=True)
    return rows


def get_all_projects(dbm, data_sender_id=None):
    if data_sender_id:
        rows = dbm.load_all_rows_in_view('projects_by_datasenders', startkey=data_sender_id, endkey=data_sender_id,
                                         include_docs=True)
        for row in rows:
            row.update({'value': row["doc"]})
        return rows
    return dbm.load_all_rows_in_view('all_projects')


def get_all_form_models(dbm, data_sender_id=None):
    if data_sender_id:
        rows = dbm.load_all_rows_in_view('projects_by_datasenders', startkey=data_sender_id, endkey=data_sender_id,
                                         include_docs=True)
        idnr_questionnaires = []
        for row in rows:
            row.update({'value': row["doc"]})
            subject_docs = get_subject_form_model_docs_of_questionnaire(dbm, FormModelDocument.wrap(row['doc']))
            for subject_doc in subject_docs:
                for questionnaire in idnr_questionnaires:
                    if subject_doc.id == questionnaire.id:
                        subject_docs.remove(subject_doc)
                        break
            idnr_questionnaires.extend(subject_docs)
        rows.extend(idnr_questionnaires)
        return rows
    return dbm.load_all_rows_in_view('all_questionnaire')


def get_subject_form_model_docs_of_questionnaire(dbm, questionnaire_doc):
    questionnaire = FormModel.new_from_doc(dbm, questionnaire_doc)
    rows = []
    for entity_question in questionnaire.entity_questions:
        rows = dbm.view.registration_form_model_by_entity_type(key=[entity_question.unique_id_type], include_docs=True)
        for row in rows:
            row.update({'value': row["doc"]})
    return rows


def get_project_id_name_map(dbm):
    project_id_name_map = {}
    rows = dbm.load_all_rows_in_view('project_names')
    for row in rows:
        project_id_name_map.update({row['value']['id']:row['value']['name']})

    project_map = sorted(project_id_name_map.items(), key=lambda(project_id, name): name.lower())

    return OrderedDict(project_map)