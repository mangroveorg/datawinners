from string import lower
from datawinners.utils import is_empty_string
from django.utils.translation import ugettext as _
from mangrove.datastore.documents import GroupDocument
from mangrove.datastore.group import Group
from mangrove.errors.MangroveException import DataObjectNotFound
from mangrove.utils.types import is_empty


def get_group_details(dbm):
    group_details = []
    rows = dbm.load_all_rows_in_view('group_by_name')
    for row in rows:
        group_details.append({'name': row['value']['name']})
    return group_details


def _check_uniqueness_of_group(dbm, group_name):
    rows = dbm.load_all_rows_in_view('group_by_name', key=lower(group_name))
    if len(rows) > 0:
        return False
    return True

def get_group_by_name(dbm, group_name):
    rows = dbm.load_all_rows_in_view('group_by_name', key=lower(group_name))
    if is_empty(rows):
        raise DataObjectNotFound('group', "Group not found")
    doc = GroupDocument.wrap(rows[0]['value'])
    return Group.new_from_doc(dbm, doc)


def create_new_group(dbm, group_name):
    is_unique = _check_uniqueness_of_group(dbm, group_name)
    if is_empty_string(group_name):
        return False, _('Group name is empty')
    if is_unique and not is_empty_string(group_name):
        new_group = Group(dbm, group_name)
        new_group.save()
        return True, _("Group %s has been added successfully.") % group_name
    return False, _("Group with same name already exists.")
