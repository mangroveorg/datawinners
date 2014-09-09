from collections import OrderedDict

from mangrove.datastore.entity_type import get_unique_id_types


def load_subject_type_with_projects(manager):
    result = OrderedDict()
    subject_types = get_unique_id_types(manager)
    for subject_type in subject_types:
        result.update({subject_type: []})
    rows = manager.view.projects_by_subject_type()
    for row in rows:
        if row.key != 'reporter':
            projects = result.get(row.key) or []
            projects.append(row.value)
            result.update({row.key: projects})

    for subject_type in subject_types:
        result[subject_type] = sorted(result[subject_type])

    return result


def get_subjects_count(manager):
    rows = manager.view.count_non_voided_entities_by_type(group=True, reduce=True)
    subject_count = {}
    for row in rows:
        subject_count[row.key[0]] = row.value
    return subject_count
