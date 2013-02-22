from datetime import datetime
from mock import patch
from mangrove.form_model.field import field_attributes, TextField, SelectField
from mangrove.form_model.form_model import NAME_FIELD, MOBILE_NUMBER_FIELD
from mangrove.transport import TransportInfo, Request
from mangrove.transport.player.player import WebPlayer
from mangrove.transport.submissions import Submission
from mangrove.utils.entity_builder import EntityBuilder
from mangrove.utils.form_model_builder import create_default_ddtype, FormModelBuilder
from mangrove.utils.test_utils.mangrove_test_case import MangroveTestCase
from project.analysis import Analysis
from project.helper import SUBMISSION_DATE_FORMAT_FOR_SUBMISSION_LOG, NOT_AVAILABLE
from project.submission_list import SubmissionList
from project.submission_router import successful_submissions
from project.tests.form_model_generator import FormModelGenerator

today = datetime.utcnow().strftime("%d.%m.%Y")

class TestSubmissionList(MangroveTestCase):
    def setUp(self):
        super(TestSubmissionList, self).setUp()
        self.org_id = 'SLX364903'
        self._prepare_subjects()

        self.transport = TransportInfo(transport="web", source="1234", destination="5678")
        self.form_model_generator = FormModelGenerator(self.manager)
        self.form_model = self.form_model_generator.form_model()

    def _prepare_submission_list_with_one_submission(self, form_model):
        submission_list = SubmissionList(form_model, self.manager, self.org_id, "all", [])
        submission_list._init_raw_values()
        self.submission_id = submission_list.submissions[0].id
        return submission_list

    def _prepare_subjects(self):
        self.ddtype = create_default_ddtype(self.manager)
        EntityBuilder(self.manager, ['clinic'], 'cli14').add_data([(NAME_FIELD, "Clinic-One", self.ddtype)]).build()
        EntityBuilder(self.manager, ['clinic'], 'cli15').add_data([(NAME_FIELD, "Clinic-Two", self.ddtype)]).build()
        EntityBuilder(self.manager, ['clinic'], 'cid001').add_data(
            [(MOBILE_NUMBER_FIELD, "919970059125", self.ddtype), (NAME_FIELD, "Ritesh", self.ddtype)]).build()

    def test_should_ignore_not_existed_option(self):
        with patch("project.submission_data.SubmissionData._get_submissions_by_type") as get_submissions:
            data = {"eid": "cli14", "RD": "01.01.2012", "SY": "A2bCZ", "BG": "D"}
            get_submissions.return_value = [Submission(self.manager,
                transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                form_code=self.form_model.form_code,
                values=data)]
            submission_list = self._prepare_submission_list_with_one_submission(self.form_model)
            try:
                statistics = submission_list.get_analysis_statistics()
            except Exception:
                self.assertTrue(False)

            q1 = ["Zhat are symptoms?", field_attributes.MULTISELECT_FIELD, 1, [
                ["Dry cough", 1],
                ["Pneumonia", 1],
                ["Rapid weight loss", 1],
                ["Memory loss", 0],
                ["Neurological disorders ", 0]]
            ]
            q2 = ["What is your blood group?", field_attributes.SELECT_FIELD, 1,
                  [["B+", 1], ["AB", 0], ["O+", 0], ["O-", 0]]]
            expected = [q1, q2]

            self.assertEqual(expected, statistics)

    def get_submission_date_in_old_format(self, submission_date):
        submission_date = datetime.strptime(submission_date, SUBMISSION_DATE_FORMAT_FOR_SUBMISSION_LOG)
        submission_date = submission_date.strftime("%d.%m.%Y")
        return submission_date

    def test_should_get_real_answer_for_select_questions_case_insensitively(self):
        with patch("project.submission_data.SubmissionData._get_submissions_by_type") as get_submissions:
            data = {"eid": "cli14", "RD": "01.01.2012", "SY": "A2bCZ", "BG": "D"}
            get_submissions.return_value = [Submission(self.manager,
                transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                form_code=self.form_model.form_code,
                values=data)]
            submission_list = self._prepare_submission_list_with_one_submission(self.form_model)
            raw_field_values = submission_list.get_raw_values()
            expected = [[self.submission_id, ('Tester Pune', 'admin', 'tester150411@gmail.com'), u'Error',
                         '-', ('Clinic-One', 'cli14'), '01.01.2012', ['Rapid weight loss', 'Dry cough', 'Pneumonia'],
                         ['B+']]]
            submission_date = self.get_submission_date_in_old_format(raw_field_values[0].pop(2))
            self.assertEqual(today, submission_date)
            self.assertEqual(expected, raw_field_values)

    def test_should_get_real_answer_for_select_questions(self):
        with patch("project.submission_data.SubmissionData._get_submissions_by_type") as get_submissions:
            data = {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"}
            get_submissions.return_value = [Submission(self.manager,
                transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                form_code=self.form_model.form_code,
                values=data)]
            submission_list = self._prepare_submission_list_with_one_submission(self.form_model)
            raw_field_values = submission_list.get_raw_values()
            expected = [[self.submission_id, (u'Tester Pune', 'admin', u'tester150411@gmail.com'), u'Error',
                         '-', ('Clinic-One', u'cli14'), '01.01.2012', ['Rapid weight loss', 'Dry cough', 'Pneumonia'],
                         ['B+']]]
            submission_date = self.get_submission_date_in_old_format(raw_field_values[0].pop(2))
            self.assertEqual(today, submission_date)
            self.assertEqual(expected, raw_field_values)

    def test_should_get_leading_part_for_non_summary_project(self):
        with patch("project.submission_data.SubmissionData._get_submissions_by_type") as get_submissions:
            data = {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"}
            get_submissions.return_value = [Submission(self.manager,
                transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                form_code=self.form_model.form_code,
                values=data)]
            submission_list = self._prepare_submission_list_with_one_submission(self.form_model)

            expected = [[self.submission_id, (u'Tester Pune', 'admin', u'tester150411@gmail.com'), u'Error',
                         '-', ('Clinic-One', u'cli14'), '01.01.2012']]
            result = submission_list.get_leading_part()
            submission_date = self.get_submission_date_in_old_format(result[0].pop(2))
            self.assertEqual(today, submission_date)
            self.assertEqual(expected, result)

            #self.form_model_generator.summary_form_model_without_rp

    def test_should_get_leading_part_for_summary_project(self):
        with patch("project.submission_data.SubmissionData._get_submissions_by_type") as get_submissions:
            data = {"eid": "rep01", "SY": "a2bc", "BG": "d"}
            get_submissions.return_value = [Submission(self.manager,
                transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                form_code=self.form_model.form_code,
                values=data)]
            submission_list = self._prepare_submission_list_with_one_submission(
                self.form_model_generator.summary_form_model_without_rp())

            expected = [[self.submission_id, (u'Tester Pune', 'admin', u'tester150411@gmail.com'), u'Error', '-']]
            result = submission_list.get_leading_part()
            submission_date = self.get_submission_date_in_old_format(result[0].pop(2))
            self.assertEqual(today, submission_date)
            self.assertEqual(expected, result)


    def test_should_get_raw_field_values(self):
        with patch("project.submission_data.SubmissionData._get_submissions_by_type") as get_submissions:
            data = {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"}
            get_submissions.return_value = [Submission(self.manager,
                transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                form_code=self.form_model.form_code,
                values=data)]
            submission_list = self._prepare_submission_list_with_one_submission(self.form_model)
            raw_field_values = submission_list.get_raw_values()
            expected = [[self.submission_id, (u'Tester Pune', 'admin', u'tester150411@gmail.com'), u'Error', '-',
                         ('Clinic-One', 'cli14'), '01.01.2012',
                         ['Rapid weight loss', 'Dry cough', 'Pneumonia'], ['B+']]]
            submission_date = self.get_submission_date_in_old_format(raw_field_values[0].pop(2))
            self.assertEqual(today, submission_date)
            self.assertEqual(expected, raw_field_values)

    def test_should_get_raw_field_values_with_status_for_all_submissions(self):
        with patch("project.submission_data.SubmissionData._get_submissions_by_type") as get_submissions:
            data = {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"}
            get_submissions.return_value = [Submission(self.manager,
                transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                form_code=self.form_model.form_code,
                values=data)]
            submission_list = self._prepare_submission_list_with_one_submission(self.form_model)
            submission_date = datetime.utcnow().strftime(SUBMISSION_DATE_FORMAT_FOR_SUBMISSION_LOG)
            raw_field_values = submission_list.get_raw_values()
            expected = [
                [self.submission_id, (u'Tester Pune', 'admin', u'tester150411@gmail.com'), submission_date, 'Error',
                 '-',
                 ('Clinic-One', 'cli14'), '01.01.2012', ['Rapid weight loss', 'Dry cough', 'Pneumonia'], ['B+']]]
            self.assertEqual(expected, raw_field_values)

    def _prepare_submission_list(self, form_model, keywords=None):
        submission_list = SubmissionList(form_model, self.manager, self.org_id, "all", [], keywords)
        submission_list._init_raw_values()
        self.submission_id = submission_list.submissions[0].id
        return submission_list

    def _prepare_analysis_list(self, form_model, keywords=None):
        analysis_list = Analysis(form_model, self.manager, self.org_id, [], keywords)
        analysis_list._init_raw_values()
        self.submission_id = analysis_list.submissions[0].id
        return analysis_list

    def test_should_get_raw_field_values_filtered_by_keyword(self):
        submissions = []
        with patch("project.submission_data.SubmissionData._get_submissions_by_type") as get_submissions:
            data_list = [{"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"},
                         {"eid": "cli15", "RD": "02.02.2012", "SY": "c", "BG": "d"}]
            for values in data_list:
                submission = Submission(self.manager,
                    transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                    form_code=self.form_model.form_code,
                    values=values)
                submissions.append(submission)
            get_submissions.return_value = submissions

            submission_list = self._prepare_submission_list(self.form_model, "Rapid")
            result = submission_list.get_raw_values()
            self.assertEqual(1, len(result))
            self.assertIn('Rapid', repr(result))

    def test_should_get_subject_list(self):
        submissions = []
        with patch("project.submission_data.SubmissionData._get_submissions_by_type") as get_submissions:
            data = [
                {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"},
                {"eid": "cli15", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"},
                {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"},
                {"1": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"}
            ]

            for values in data:
                submission = Submission(self.manager,
                    transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                    form_code=self.form_model.form_code,
                    values=values)
                submissions.append(submission)
            get_submissions.return_value = submissions

            submission_list = self._prepare_submission_list(self.form_model)
            subject_list = submission_list.get_subjects()
            expected = [('Clinic-One', u'cli14'), ('Clinic-Two', u'cli15'),(NOT_AVAILABLE, str(None))]
            self.assertEqual(expected, subject_list)

    def test_should_get_datasender_list(self):
        with patch("project.submission_data.SubmissionData._get_submissions_by_type") as get_submissions:
            data = {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"}
            get_submissions.return_value = [Submission(self.manager,
                transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                form_code=self.form_model.form_code,
                values=data)]
            submission_list = self._prepare_submission_list_with_one_submission(self.form_model)
            data_sender_list = submission_list.get_data_senders()
            expected = [('Tester Pune', 'admin', 'tester150411@gmail.com')]
            self.assertEqual(expected, data_sender_list)

    def test_should_get_statistic_result_for_analysis_page(self):
        """
            Function to test getting statistic result.
            question name ordered by field
            options ordered by count(desc),option(alphabetic)
            total = submission count of this question
        """
        submissions = []
        with patch("datawinners.project.submission_data.SubmissionData._get_submissions_by_type") as get_submissions:
            data = [{"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"},
                    {"eid": "cli14", "RD": "01.01.2012", "BG": "c"}
            ]
            for values in data:
                submission = Submission(self.manager,
                    transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                    form_code=self.form_model.form_code,
                    values=values)
                submissions.append(submission)
            get_submissions.return_value = submissions
            analysis_list = self._prepare_analysis_list(self.form_model)
            statistics = analysis_list.get_analysis_statistics()
            q1 = ["Zhat are symptoms?", field_attributes.MULTISELECT_FIELD, 1, [
                ["Dry cough", 1],
                ["Pneumonia", 1],
                ["Rapid weight loss", 1],
                ["Memory loss", 0],
                ["Neurological disorders ", 0]]
            ]
            q2 = ["What is your blood group?", field_attributes.SELECT_FIELD, 2,
                  [["AB", 1], ["B+", 1], ["O+", 0], ["O-", 0]]]
            expected = [q1, q2]
            self.assertEqual(expected, statistics)

    def submit_data(self, post_data):
        WebPlayer(self.manager).accept(Request(message=post_data, transportInfo=self.transport))

    def _edit_fields(self, form_model, *updated_fields):
        fields = []
        for field in form_model.fields:
            need_update = False
            for update in updated_fields:
                if update.code == field.code:
                    need_update = True
                    fields.append(update)
            if not need_update:
                fields.append(field)

        form_model.create_snapshot()
        form_model.delete_all_fields()
        [form_model.add_field(each) for each in fields]
        form_model.save()

    def test_should_get_statistic_result_after_answer_type_changed_from_word_to_mc(self):
        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associated entity?",
            entity_question_flag=True, ddtype=self.ddtype)
        blood_type_field = TextField(label="What is your blood group?", code="BG", name="What is your blood group?",
            ddtype=self.ddtype)

        form_model = FormModelBuilder(self.manager, ['clinic'], form_code='cli001').add_fields(eid_field,
            blood_type_field).build()
        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'BG': 'unknown'})

        blood_type_field = SelectField(label="What is your blood group?", code="BG", name="What is your blood group?",
            options=[("O+", "a"), ("O-", "b"), ("AB", "c"), ("B+", "d")], single_select_flag=False, ddtype=self.ddtype)
        self._edit_fields(form_model, blood_type_field)
        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'BG': 'ab'})
        with patch("datawinners.project.submission_data.SubmissionData._get_submissions_by_type") as get_submissions:
            get_submissions.return_value = successful_submissions(self.manager, form_model.form_code)
            analysis_list = Analysis(form_model,self.manager,self.org_id,[])
            analysis_list._init_raw_values()
            statistics = analysis_list.get_analysis_statistics()

            expected = [["What is your blood group?", field_attributes.MULTISELECT_FIELD, 2,
                         [["O+", 1], ["O-", 1], ['unknown', 1], ["AB", 0], ["B+", 0]]]]
            self.assertEqual(expected, statistics)

    def test_should_get_statistic_result_after_option_value_changed(self):
        """
            Function to test getting statistic result of submissions after option value changed.
            question name ordered by field
            options ordered by count(desc),option(alphabetic)
            total = submission count of this question
        """
        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associated entity?",
            entity_question_flag=True, ddtype=self.ddtype)
        blood_type_field = SelectField(label="What is your blood group?", code="BG", name="What is your blood group?",
            options=[("Type 1", "a"), ("Type 2", "b")], single_select_flag=True, ddtype=self.ddtype)

        form_model = FormModelBuilder(self.manager, ['clinic'], form_code='cli001').add_fields(eid_field,
            blood_type_field).build()

        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'BG': 'a'})

        blood_type_field = SelectField(label="What is your blood group?", code="BG", name="What is your blood group?",
            options=[("O+", "a"), ("O-", "b"), ("AB", "c"), ("B+", "d")], single_select_flag=True, ddtype=self.ddtype)
        self._edit_fields(form_model, blood_type_field)
        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'BG': 'a'})
        with patch("datawinners.project.submission_data.SubmissionData._get_submissions_by_type") as get_submissions:
            get_submissions.return_value = successful_submissions(self.manager, form_model.form_code)
            analysis_list = self._prepare_analysis_list(form_model)
            statistics = analysis_list.get_analysis_statistics()

            expected = [["What is your blood group?", field_attributes.SELECT_FIELD, 2,
                         [["O+", 1], ['Type 1', 1], ["AB", 0], ["B+", 0], ["O-", 0]]]]
            self.assertEqual(expected, statistics)

    def test_should_get_default_sort_order_of_submission_date_for_subject_project_with_rp(self):
        with patch("datawinners.project.submission_data.SubmissionData._get_submissions_by_type") as get_submissions:
            data = {"eid": "cli14", "RD": "01.01.2012", "SY": "A2bCZ", "BG": "D"}
            get_submissions.return_value = [Submission(self.manager,
                transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                form_code=self.form_model.form_code,
                values=data)]
            analyzer = self._prepare_analysis_list(self.form_model)
            default_sort_order = analyzer.get_default_sort_order()
            self.assertEqual([[3, 'desc']], default_sort_order)

    def test_should_get_default_sort_order_of_submission_date_for_subject_project_without_rp(self):
        self.form_model = self.form_model_generator.subject_form_model_without_rp()
        with patch("datawinners.project.submission_data.SubmissionData._get_submissions_by_type") as get_submissions:
            data = {"eid": "cli14", "RD": "01.01.2012", "SY": "A2bCZ", "BG": "D"}
            get_submissions.return_value = [Submission(self.manager,
                transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                form_code=self.form_model.form_code,
                values=data)]
            analyzer = self._prepare_analysis_list(self.form_model)
            default_sort_order = analyzer.get_default_sort_order()
            self.assertEqual([[2, 'desc']], default_sort_order)
