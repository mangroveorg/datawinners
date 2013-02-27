from django.contrib.auth.models import User
from django.utils.translation import ugettext
from accountmanagement.models import NGOUserProfile
from datawinners.messageprovider.messages import SMS
from datawinners.project.data_sender import DataSender
from datawinners.project.helper import NOT_AVAILABLE_DS

class DataSenderHelper(object):
    def __init__(self, dbm, form_code=None):
        self.manager = dbm
        self.form_code = form_code

    def get_all_data_senders_ever_submitted(self, org_id):
        submission_data_sender_info_list = self._get_all_submission_data_sender_info()

        sms_data_sender_list = self._get_all_sms_data_senders()
        non_sms_data_sender_list = list_data_sender(org_id)

        sms_data_senders = self._get_all_data_senders_with_submission(sms_data_sender_list,
            submission_data_sender_info_list, filter_function=self._is_submitted_via_sms)
        non_sms_data_senders = self._get_all_data_senders_with_submission(non_sms_data_sender_list,
            submission_data_sender_info_list, filter_function=self._is_not_submitted_via_sms)

        return self._combine_channels(non_sms_data_senders.union(sms_data_senders))

    def _combine_channels(self, data_senders):
        keys = {x.name for x in data_senders}
        grouped_data_senders = [filter(lambda x: x.name == key, data_senders) for key in keys]

        return sorted(
            [DataSender(map(lambda x: x.source, a), a[0].name, a[0].reporter_id) for a in grouped_data_senders],
            key=lambda ds: ds.name)

    def combine_channels_for_tuple(self, data_senders_tuple_list):
        data_senders = [DataSender.from_tuple(data_sender_tuple) for data_sender_tuple in data_senders_tuple_list]
        return map(lambda d: d.to_tuple(), self._combine_channels(data_senders))

    def _is_submitted_via_sms(self, data_sender_info):
        return data_sender_info[1] == SMS

    def _is_not_submitted_via_sms(self, data_sender_info):
        return not self._is_submitted_via_sms(data_sender_info)

    def _get_all_data_senders_with_submission(self, data_sender_list, submission_data_sender_info_list,
                                              filter_function):
        data_sender_info_list = filter(filter_function, submission_data_sender_info_list)
        source_to_data_sender_dict = {each.source: each for each in data_sender_list}

        return {source_to_data_sender_dict.get(data_sender_info[2],
            DataSender(data_sender_info[2], ugettext(NOT_AVAILABLE_DS), None)) for data_sender_info in
                data_sender_info_list}

    def _get_data_sender_for_sms(self, submission):
        return tuple(self._data_sender_by_mobile(submission.source) + [submission.source])

    def _get_data_sender_for_not_sms(self, submission, org_id):
        try:
            data_sender = data_sender_by_email(org_id, submission.source)
        except:
            data_sender = (ugettext(NOT_AVAILABLE_DS), None, submission.source)

        return data_sender

    def _data_sender_by_mobile(self, mobile):
        rows = self.manager.load_all_rows_in_view("datasender_by_mobile", startkey=[mobile], endkey=[mobile, {}])
        return rows[0].key[1:] if len(rows) > 0 else [ugettext(NOT_AVAILABLE_DS), None]

    def _get_all_sms_data_senders(self):
        rows = self.manager.load_all_rows_in_view("datasender_by_mobile")

        return map(lambda x: DataSender(*x.key), rows)

    def _get_all_submission_data_sender_info(self):
        return [each.key for each in
                self.manager.load_all_rows_in_view("submission_data_sender_info", startkey=[self.form_code],
                    endkey=[self.form_code, {}], group_level=3)]

def combine_channels_for_tuple(data_senders_tuple_list):
    data_senders = [DataSender.from_tuple(data_sender_tuple) for data_sender_tuple in data_senders_tuple_list]
    return map(lambda d: d.to_tuple(), combine_channels(data_senders))

def combine_channels(data_senders):
    keys = {x.name for x in data_senders}
    grouped_data_senders = [filter(lambda x: x.name == key, data_senders) for key in keys]

    return sorted([DataSender(map(lambda x: x.source, a), a[0].name, a[0].reporter_id) for a in grouped_data_senders],
        key=lambda ds: ds.name)

def get_data_sender(manager, org_id, submission):
    if submission.channel == 'sms':
        data_sender = get_data_sender_for_sms(manager, submission)
    else:
        data_sender = get_data_sender_for_not_sms(submission, org_id)

    return data_sender if data_sender[0] != "TEST" else ("TEST", "n/a", "TEST")

def get_data_sender_for_sms(manager, submission):
    return tuple(data_sender_by_mobile(manager, submission.source) + [submission.source])

def get_data_sender_for_not_sms(submission, org_id):
    try:
        data_sender = data_sender_by_email(org_id, submission.source)
    except:
        data_sender = (ugettext(NOT_AVAILABLE_DS), None, submission.source)
    return data_sender

def data_sender_by_mobile(manager, mobile):
    rows = manager.load_all_rows_in_view("datasender_by_mobile", startkey=[mobile], endkey=[mobile, {}])
    return rows[0].key[1:] if len(rows) > 0 else [ugettext(NOT_AVAILABLE_DS), None]

def data_sender_by_email(org_id, email):
    data_sender = User.objects.get(email=email)
    reporter_id = NGOUserProfile.objects.filter(user=data_sender, org_id=org_id)[0].reporter_id or "admin"
    return data_sender.get_full_name(), reporter_id, email

def list_data_sender(org_id):
    ngo_user_profiles = list(NGOUserProfile.objects.filter(org_id=org_id).all())
    return [DataSender(each.user.email, each.user.get_full_name(), each.reporter_id or "admin") for each in
            ngo_user_profiles]