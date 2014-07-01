import unittest
from mock import Mock, patch
from datawinners.common.lang.utils import ERROR_MSG_MISMATCHED_SYS_VARIABLE
from datawinners.common.lang.views import verify_inconsistency_in_system_variables
from mangrove.datastore.database import DatabaseManager


class TestLanguageViews(unittest.TestCase):
    def test_should_return_empty_dict_if_there_is_no_mismatch_in_system_variables(self):
        dbm = Mock(spec=DatabaseManager)
        language = 'en'
        incoming_message = {'reply_success_submission': 'Thank you {<{var1}>}.{<{var2}>}.',
                            'reply_incorrect_answers': 'Error {<{var1}>}. incorrect error {<{var2}>}. {<{var3}>}'}
        with patch('datawinners.common.lang.views.questionnaire_customized_message_details') as existing_message_dict:
            existing_message_dict.return_value = [
                {'message': 'Thank you {<{var1}>}. datasender {<{var2}>}.', 'code': 'reply_success_submission',
                 'title': u'Successful Submission'},
                {'message': 'Error {<{var1}>}. incorrect error {<{var2}>}. {<{var3}>}', 'code': 'reply_incorrect_answers',
                 'title': u'Submission with an Error'}]

            corrected_list, errored_message_list = verify_inconsistency_in_system_variables(dbm, incoming_message,
                                                                                          language)
            self.assertEqual([], corrected_list)

    def test_should_return_corresponding_msg_code_if_there_is_mismatch_in_system_variables(self):
        dbm = Mock(spec=DatabaseManager)
        language = 'en'
        incoming_message = {'reply_success_submission': 'Thank you ',
                            'reply_incorrect_answers': 'Error {<{var1}>}. incorrect error {<{var2}>}. {<{var3}>}'}
        with patch('datawinners.common.lang.views.questionnaire_customized_message_details') as existing_message_dict:
            existing_message_dict.return_value = [
                {'message': 'Thank you {<{var1}>}. datasender {<{var2}>}.', 'code': 'reply_success_submission',
                 'title': u'Successful Submission'},
                {'message': 'Error {<{var1}>}. incorrect error {<{var2}>}. {<{var3}>}', 'code': 'reply_incorrect_answers',
                 'title': u'Submission with an Error'}]

            expected = [
                {'message': 'Thank you {<{var1}>}. datasender {<{var2}>}.', 'code': 'reply_success_submission',
                 'title': u'Successful Submission', 'valid': False, 'error': ERROR_MSG_MISMATCHED_SYS_VARIABLE},
                {'message': 'Error {<{var1}>}. incorrect error {<{var2}>}. {<{var3}>}', 'code': 'reply_incorrect_answers',
                 'title': u'Submission with an Error'}]

            corrected_list, errored_message_list = verify_inconsistency_in_system_variables(dbm, incoming_message,
                                                                                          language)
            self.assertListEqual(expected, corrected_list)

    def test_should_get_account_wide_message_list_if_account_wide_sms_flag_is_set(self):
        dbm = Mock(spec=DatabaseManager)
        with patch('datawinners.common.lang.views.account_wide_customized_message_details') as account_wide_customized_message_details:
            verify_inconsistency_in_system_variables(dbm, {},is_account_wid_sms=True)
            account_wide_customized_message_details.assert_called_once_with(dbm)


