from datawinners.accountmanagement.models import NGOUserProfile
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


def remove_test_datasenders(datasender_list):
    for datasender in datasender_list:
        if datasender["short_code"] == "test":
            index = datasender_list.index(datasender)
            del datasender_list[index]


def get_user_profile_by_reporter_id(reporter_id, user):
    org_id = NGOUserProfile.objects.get(user=user).org_id
    user_profile = NGOUserProfile.objects.filter(reporter_id=reporter_id, org_id=org_id)
    return user_profile[0] if len(user_profile) else None


def get_datasender_user_detail(datasender, user):
    user_profile = get_user_profile_by_reporter_id(datasender['short_code'], user)

    datasender["is_user"] = False
    if user_profile:
        datasender_user_groups = list(user_profile.user.groups.values_list('name', flat=True))
        if "NGO Admins" in datasender_user_groups or "Project Managers" in datasender_user_groups \
            or "Read Only Users" in datasender_user_groups:
            datasender["is_user"] = True
        datasender['email'] = user_profile.user.email
        datasender['devices'] = "SMS,Web,Smartphone"
    else:
        datasender['email'] = None
        datasender['devices'] = "SMS"