from collections import OrderedDict
from mangrove.datastore.documents import FormModelDocument
from mangrove.form_model.form_model import FormModel, get_form_model_by_entity_type


def get_all_projects_for_datasender(dbm, data_sender_id):
    rows = dbm.load_all_rows_in_view('projects_by_datasenders', key=data_sender_id, include_docs=True)
    return rows


def get_all_projects(dbm, data_sender_id=None):
    if data_sender_id:
        projects = []
        rows = dbm.load_all_rows_in_view('projects_by_datasenders', startkey=data_sender_id, endkey=data_sender_id,
                                         include_docs=True)
        for row in rows:
            row.update({'value': row["doc"]})
            projects.append(row)
        return projects
    return dbm.load_all_rows_in_view('all_projects')


def remove_poll_questionnaires(rows):
    projects = []
    for row in rows:
        if 'is_poll' not in row['value'] or row['value']['is_poll'] is False:
            projects.append(row)
    return projects


def get_all_form_models(dbm, data_sender_id=None):
    questionnaires = []
    if data_sender_id:
        rows = dbm.load_all_rows_in_view('projects_by_datasenders', startkey=data_sender_id, endkey=data_sender_id,
                                         include_docs=True)
        idnr_questionnaires = []
        for row in rows:
            row.update({'value': row["doc"]})
            subject_docs = get_subject_form_model_docs_of_questionnaire(dbm, FormModelDocument.wrap(row['doc']))
            duplicate_docs = []
            for subject_doc in subject_docs:
                for questionnaire in idnr_questionnaires:
                    if subject_doc.id == questionnaire.id:
                        duplicate_docs.append(subject_doc)
            for duplicate_doc in duplicate_docs:
                if duplicate_doc in subject_docs:
                    subject_docs.remove(duplicate_doc)
            idnr_questionnaires.extend(subject_docs)
        rows.extend(idnr_questionnaires)
    else:
        rows = dbm.load_all_rows_in_view('all_questionnaire')
    for row in rows:
        if 'is_poll' not in row['value'] or row['value']['is_poll'] is False:
            questionnaires.append(row)

    return questionnaires


def get_subject_form_model_docs_of_questionnaire(dbm, questionnaire_doc):
    questionnaire = FormModel.new_from_doc(dbm, questionnaire_doc)
    subject_form_model_docs = []
    for entity_question in questionnaire.entity_questions:
        rows = dbm.view.registration_form_model_by_entity_type(key=[entity_question.unique_id_type], include_docs=True)
        for row in rows:
            row.update({'value': row["doc"]})
        subject_form_model_docs.extend(rows)
    return subject_form_model_docs


def get_project_id_name_map(dbm):
    project_id_name_map = {}
    rows = dbm.load_all_rows_in_view('project_names')
    for row in rows:
        if 'is_poll' not in row['value'] or row['value']['is_poll'] is False:
            project_id_name_map.update({row['value']['id']:row['value']['name']})

    project_map = sorted(project_id_name_map.items(), key=lambda(project_id, name): name.lower())

    return OrderedDict(project_map)