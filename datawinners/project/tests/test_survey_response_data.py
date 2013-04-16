from datetime import datetime
from mangrove.transport.player.new_players import WebPlayerV2
from mock import patch, Mock
from mangrove.form_model.field import field_attributes, TextField, SelectField, DateField, IntegerField, GeoCodeField, ExcelDate
from mangrove.form_model.form_model import NAME_FIELD, MOBILE_NUMBER_FIELD, FormModel
from mangrove.transport.contract.transport_info import TransportInfo
from mangrove.transport.contract.request import Request
from mangrove.utils.entity_builder import EntityBuilder
from mangrove.utils.form_model_builder import create_default_ddtype, FormModelBuilder
from mangrove.utils.test_utils.mangrove_test_case import MangroveTestCase
from datawinners.project.analysis import Analysis
from datawinners.project.analysis_for_excel import AnalysisForExcel
from datawinners.project.helper import SUBMISSION_DATE_FORMAT_FOR_SUBMISSION, NOT_AVAILABLE
from datawinners.project.survey_response_list import SurveyResponseList
from datawinners.project.survey_response_router import successful_survey_responses
from datawinners.project.tests.form_model_generator import FormModelGenerator
from mangrove.transport.contract.survey_response import SurveyResponse

today = datetime.utcnow().strftime("%d.%m.%Y")

class TestSurveyResponseData(MangroveTestCase):
    def setUp(self):
        super(TestSurveyResponseData, self).setUp()
        self.org_id = 'SLX364903'
        self._prepare_subjects()

        self.transport = TransportInfo(transport="web", source="1234", destination="5678")
        self.form_model_generator = FormModelGenerator(self.manager)
        self.form_model = self.form_model_generator.form_model()

    def _prepare_submission_list_with_one_submission(self, form_model):
        submission_list = SurveyResponseList(form_model, self.manager, self.org_id, "all", [])
        self.submission_id = submission_list.filtered_survey_responses[0].id
        return submission_list

    def _prepare_subjects(self):
        self.ddtype = create_default_ddtype(self.manager)
        EntityBuilder(self.manager, ['clinic'], 'cli14').add_data([(NAME_FIELD, "Clinic-One", self.ddtype)]).build()
        EntityBuilder(self.manager, ['clinic'], 'cli15').add_data([(NAME_FIELD, "Clinic-Two", self.ddtype)]).build()
        EntityBuilder(self.manager, ['clinic'], 'cid001').add_data(
            [(MOBILE_NUMBER_FIELD, "919970059125", self.ddtype), (NAME_FIELD, "Ritesh", self.ddtype)]).build()

    def test_should_ignore_not_existed_option(self):
        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            data = {"eid": "cli14", "RD": "01.01.2012", "SY": "A2bCZ", "BG": "D"}
            get_submissions.return_value = [SurveyResponse(self.manager,
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
        submission_date = datetime.strptime(submission_date, SUBMISSION_DATE_FORMAT_FOR_SUBMISSION)
        submission_date = submission_date.strftime("%d.%m.%Y")
        return submission_date

    def test_should_get_real_answer_for_select_questions_case_insensitively(self):
        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            data = {"eid": "cli14", "RD": "01.01.2012", "SY": "A2bCZ", "BG": "D"}
            get_submissions.return_value = [SurveyResponse(self.manager,
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
        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            data = {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"}
            get_submissions.return_value = [SurveyResponse(self.manager,
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
        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            data = {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"}
            get_submissions.return_value = [SurveyResponse(self.manager,
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
        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            data = {"eid": "rep01", "SY": "a2bc", "BG": "d"}
            get_submissions.return_value = [SurveyResponse(self.manager,
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
        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            data = {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"}
            get_submissions.return_value = [SurveyResponse(self.manager,
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
        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            data = {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"}
            get_submissions.return_value = [SurveyResponse(self.manager,
                transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                form_code=self.form_model.form_code,
                values=data)]
            submission_list = self._prepare_submission_list_with_one_submission(self.form_model)
            submission_date = datetime.utcnow().strftime(SUBMISSION_DATE_FORMAT_FOR_SUBMISSION)
            raw_field_values = submission_list.get_raw_values()
            expected = [
                [self.submission_id, (u'Tester Pune', 'admin', u'tester150411@gmail.com'), submission_date, 'Error',
                 '-',
                 ('Clinic-One', 'cli14'), '01.01.2012', ['Rapid weight loss', 'Dry cough', 'Pneumonia'], ['B+']]]
            self.assertEqual(expected, raw_field_values)

    def _prepare_submission_list(self, form_model, keywords=None):
        submission_list = SurveyResponseList(form_model, self.manager, self.org_id, "all", [], keywords)
        self.submission_id = submission_list.filtered_survey_responses[0].id
        return submission_list

    def _prepare_analysis_list(self, form_model, keywords=None):
        analysis_list = Analysis(form_model, self.manager, self.org_id, [], keywords)
        self.submission_id = analysis_list.filtered_survey_responses[0].id
        return analysis_list

    def test_should_get_raw_field_values_filtered_by_keyword(self):
        submissions = []
        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            data_list = [{"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"},
                         {"eid": "cli15", "RD": "02.02.2012", "SY": "c", "BG": "d"}]
            for values in data_list:
                submission = SurveyResponse(self.manager,
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
        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            data = [
                {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"},
                {"eid": "cli15", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"},
                {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"},
                {"1": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"}
            ]

            for values in data:
                submission = SurveyResponse(self.manager,
                    transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                    form_code=self.form_model.form_code,
                    values=values)
                submissions.append(submission)
            get_submissions.return_value = submissions

            submission_list = self._prepare_submission_list(self.form_model)
            subject_list = submission_list.get_subjects()
            expected = [('Clinic-One', u'cli14'), ('Clinic-Two', u'cli15'), (NOT_AVAILABLE, str(None))]
            self.assertEqual(expected, subject_list)

    def test_should_get_datasender_list(self):
        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            data = {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"}
            get_submissions.return_value = [SurveyResponse(self.manager,
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
        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            data = [{"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"},
                    {"eid": "cli14", "RD": "01.01.2012", "BG": "c"}
            ]
            for values in data:
                submission = SurveyResponse(self.manager,
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

    def submit_survey_response(self, post_data):
        WebPlayerV2(self.manager).add_survey_response(Request(message=post_data, transportInfo=self.transport))

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
        self.submit_survey_response({'form_code': 'cli001', 'EID': 'cid001', 'BG': 'unknown'})

        blood_type_field = SelectField(label="What is your blood group?", code="BG", name="What is your blood group?",
            options=[("O+", "a"), ("O-", "b"), ("AB", "c"), ("B+", "d")], single_select_flag=False, ddtype=self.ddtype)
        self._edit_fields(form_model, blood_type_field)
        self.submit_survey_response({'form_code': 'cli001', 'EID': 'cid001', 'BG': 'ab'})
        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            get_submissions.return_value = successful_survey_responses(self.manager, form_model.form_code)
            analysis_list = Analysis(form_model, self.manager, self.org_id, [])
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

        self.submit_survey_response({'form_code': 'cli001', 'EID': 'cid001', 'BG': 'a'})

        blood_type_field = SelectField(label="What is your blood group?", code="BG", name="What is your blood group?",
            options=[("O+", "a"), ("O-", "b"), ("AB", "c"), ("B+", "d")], single_select_flag=True, ddtype=self.ddtype)
        self._edit_fields(form_model, blood_type_field)
        self.submit_survey_response({'form_code': 'cli001', 'EID': 'cid001', 'BG': 'a'})
        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            get_submissions.return_value = successful_survey_responses(self.manager, form_model.form_code)
            analysis_list = self._prepare_analysis_list(form_model)
            statistics = analysis_list.get_analysis_statistics()

            expected = [["What is your blood group?", field_attributes.SELECT_FIELD, 2,
                         [["O+", 1], ['Type 1', 1], ["AB", 0], ["B+", 0], ["O-", 0]]]]
            self.assertEqual(expected, statistics)

    def test_should_get_default_sort_order_of_submission_date_for_subject_project_with_rp(self):
        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            data = {"eid": "cli14", "RD": "01.01.2012", "SY": "A2bCZ", "BG": "D"}
            get_submissions.return_value = [SurveyResponse(self.manager,
                transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                form_code=self.form_model.form_code,
                values=data)]
            analyzer = self._prepare_analysis_list(self.form_model)
            default_sort_order = analyzer.get_default_sort_order()
            self.assertEqual([[3, 'desc']], default_sort_order)

    def test_should_get_default_sort_order_of_submission_date_for_subject_project_without_rp(self):
        self.form_model = self.form_model_generator.subject_form_model_without_rp()
        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            data = {"eid": "cli14", "RD": "01.01.2012", "SY": "A2bCZ", "BG": "D"}
            get_submissions.return_value = [SurveyResponse(self.manager,
                transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                form_code=self.form_model.form_code,
                values=data)]
            analyzer = self._prepare_analysis_list(self.form_model)
            default_sort_order = analyzer.get_default_sort_order()
            self.assertEqual([[2, 'desc']], default_sort_order)

    def test_should_get_old_answer_for_submissions_which_is_submitted_before_MC_changed_to_other(self):
        """
        Function to test get old answer for submissions which is submitted before answer type changed from multiple choice/single choice to other type(word, number, date, GPS)
        """
        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associated entity?",
            entity_question_flag=True, ddtype=self.ddtype)
        rp_field = DateField(label="Report date", code="RD", name="What is reporting date?", date_format="dd.mm.yyyy",
            event_time_field_flag=True, ddtype=self.ddtype)
        symptoms_field = SelectField(label="Zhat are symptoms?", code="SY", name="Zhat are symptoms?",
            options=[("Rapid weight loss", "a"), ("Dry cough", "b"), ("Pneumonia", "c"),
                     ("Memory loss", "d"), ("Neurological disorders ", "e")], single_select_flag=False,
            ddtype=self.ddtype)
        blood_type_field = SelectField(label="What is your blood group?", code="BG", name="What is your blood group?",
            options=[("O+", "a"), ("O-", "b"), ("AB", "c"), ("B+", "d")], single_select_flag=True, ddtype=self.ddtype)

        form_model = FormModelBuilder(self.manager, ['clinic'], form_code='cli001').add_fields(eid_field, rp_field,
            symptoms_field, blood_type_field).build()

        self.submit_survey_response({'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.12.2012', 'SY': 'ab', 'BG': 'b'})
        self._edit_fields(form_model,
            IntegerField(label="Zhat are symptoms?", code="SY", name="Zhat are symptoms?", ddtype=self.ddtype))

        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as _get_survey_responses_by_status:
            _get_survey_responses_by_status.return_value = successful_survey_responses(self.manager,
                form_model.form_code)
            analyzer = self._prepare_analysis_list(form_model)
            values = analyzer.get_raw_values()

            self.assertEqual([['Rapid weight loss', 'Dry cough'], ['O-']], values[0][5:])

    def test_should_get_old_answer_for_submissions_which_is_submitted_before_other_changed_to_MC(self):
        """
        Function to test get old answer for submissions which is submitted before answer type changed from other type(word, number, date, GPS) to multiple choice/single choice
        """
        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associated entity?",
            entity_question_flag=True, ddtype=self.ddtype)
        rp_field = DateField(label="Report date", code="RD", name="What is reporting date?", date_format="dd.mm.yyyy",
            event_time_field_flag=True, ddtype=self.ddtype)
        symptoms_field = TextField(label="Zhat are symptoms?", code="SY", name="Zhat are symptoms?", ddtype=self.ddtype)
        blood_type_field = SelectField(label="What is your blood group?", code="BG", name="What is your blood group?",
            options=[("O+", "a"), ("O-", "b"), ("AB", "c"), ("B+", "d")], single_select_flag=True, ddtype=self.ddtype)

        form_model = FormModelBuilder(self.manager, ['clinic'], form_code='cli001').add_fields(eid_field, rp_field,
            symptoms_field, blood_type_field).build()
        self.submit_survey_response(
            {'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.12.2012', 'SY': 'Fever', 'BG': 'b'})

        symptoms_field = SelectField(label="Zhat are symptoms?", code="SY", name="Zhat are symptoms?",
            options=[("Rapid weight loss", "a"), ("Dry cough", "b"), ("Pneumonia", "c"),
                     ("Memory loss", "d"), ("Neurological disorders ", "e")], single_select_flag=False,
            ddtype=self.ddtype)
        self._edit_fields(form_model, symptoms_field)
        self.submit_survey_response({'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.12.2012', 'SY': 'ab', 'BG': 'b'})
        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            get_submissions.return_value = successful_survey_responses(self.manager, form_model.form_code)
            analyzer = self._prepare_analysis_list(form_model)
            values = analyzer.get_raw_values()

            self.assertEqual([['Rapid weight loss', 'Dry cough'], ['O-']], values[0][5:])
            self.assertEqual(['Fever', ['O-']], values[1][5:])

    def test_should_show_previous_submissions_in_old_format_after_change_date_format(self):
        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associated entity?",
            entity_question_flag=True, ddtype=self.ddtype)
        rp_field = DateField(label="Report date", code="RD", name="What is reporting date?", date_format="dd.mm.yyyy",
            event_time_field_flag=True, ddtype=self.ddtype)

        form_model = FormModelBuilder(self.manager, ['clinic'], form_code='cli001').add_fields(eid_field,
            rp_field).build()

        self.submit_survey_response({'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.12.2012'})

        rp_field = DateField(label="Report date", code="RD", name="What is reporting date?", date_format="mm.yyyy",
            event_time_field_flag=True, ddtype=self.ddtype)
        self._edit_fields(form_model, rp_field)
        self.submit_survey_response({'form_code': 'cli001', 'EID': 'cid001', 'RD': '08.2012'})

        rp_field = DateField(label="Report date", code="RD", name="What is reporting date?", date_format="mm.dd.yyyy",
            event_time_field_flag=True, ddtype=self.ddtype)
        self._edit_fields(form_model, rp_field)
        self.submit_survey_response({'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.24.2012'})

        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            get_submissions.return_value = successful_survey_responses(self.manager, form_model.form_code)
            analyzer = self._prepare_analysis_list(form_model)
            values = analyzer.get_raw_values()

            reporting_periods = map(lambda value: value[2], values)
            self.assertIn('08.2012', reporting_periods)
            self.assertIn('12.12.2012', reporting_periods)
            self.assertIn('12.24.2012', reporting_periods)

    def test_should_should_get_fields_values_after_question_count_changed(self):
        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associated entity?",
            entity_question_flag=True, ddtype=self.ddtype)
        rp_field = DateField(label="Report date", code="RD", name="What is reporting date?", date_format="dd.mm.yyyy",
            event_time_field_flag=True, ddtype=self.ddtype)
        symptoms_field = TextField(label="Zhat are symptoms?", code="SY", name="Zhat are symptoms?", ddtype=self.ddtype)
        gps = TextField(label="What is your blood group?", code="GPS", name="What is your gps?", ddtype=self.ddtype)
        form_model = FormModelBuilder(self.manager, ['clinic'], form_code='cli001').add_fields(eid_field, rp_field,
            symptoms_field, gps).build()

        self.submit_survey_response(
            {'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.12.2012', 'SY': 'Fever', 'GPS': 'NewYork'})

        form_model.create_snapshot()
        form_model.delete_field("SY")
        form_model.save()

        self.submit_survey_response({'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.12.2012', 'GPS': '1,1'})
        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            get_submissions.return_value = successful_survey_responses(self.manager, form_model.form_code)
            analyzer = self._prepare_analysis_list(form_model)
            values = analyzer.get_raw_values()

            self.assertEqual(['1,1'], values[0][5:])
            self.assertEqual(['NewYork'], values[1][5:])

    def test_should_prepare_data_for_excel(self):
        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associated entity?",
            entity_question_flag=True, ddtype=self.ddtype)
        blood_type_field = SelectField(label="What is your blood group?", code="BG", name="What is your blood group?",
            options=[("Type 1", "a"), ("Type 2", "b")], single_select_flag=True, ddtype=self.ddtype)
        rp_field = DateField(label="Report date", code="RD", name="What is reporting date?", date_format="dd.mm.yyyy",
            event_time_field_flag=True, ddtype=self.ddtype)
        age_field = IntegerField(label="Fathers age", code="FA", name="Zhat is your father's age?",
            ddtype=self.ddtype)
        gps_field = GeoCodeField(label="What is your gps?", code="GPS", name="What is your gps?", ddtype=self.ddtype)

        form_model = FormModelBuilder(self.manager, ['clinic'], form_code='cli001').add_fields(eid_field,
            blood_type_field, rp_field, age_field, gps_field).build()

        post_data = {'form_code': 'cli001', 'EID': 'cid001', 'BG': 'a', 'RD': '12.11.2013', 'FA': '45',
                     'GPS': '12.74,77.45'}
        self.submit_survey_response(post_data)

        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            get_submissions.return_value = [SurveyResponse(self.manager,
                transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                form_code=form_model.form_code,
                values=post_data)]
            analyzer = AnalysisForExcel(form_model, self.manager, self.org_id, [])
            excel_values = analyzer.get_raw_values()
            self.assertEqual(excel_values[0][1], 'Ritesh')
            self.assertEqual(excel_values[0][2], u'cid001')
            self.assertEqual(excel_values[0][3], ExcelDate(datetime.strptime('12.11.2013', '%d.%m.%Y'), 'dd.mm.yyyy'))
            self.assertEqual(excel_values[0][5], u'Tester Pune')
            self.assertEqual(excel_values[0][6], 'admin')
            self.assertEqual(excel_values[0][8], 45.0)
            self.assertEqual(excel_values[0][9], 12.74)
            self.assertEqual(excel_values[0][10], 77.45)

    def create_submission_list_instance(self):
        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            data = {"eid": "cli14", "RD": "01.01.2012", "SY": "A2bCZ", "BG": "D"}
            get_submissions.return_value = [SurveyResponse(self.manager,
                transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                form_code=self.form_model.form_code,
                values=data)]
            submission_list = self._prepare_submission_list_with_one_submission(self.form_model)
        return submission_list

    def test_should_give_answers_values_according_to_question_code(self):
        submission_list = self.create_submission_list_instance()
        answers = {'EID': 'answer', 'other_value': 'other_value'}
        question_field = TextField(label="What is associated entity?", code="EID", name="What is associated entity?",
            entity_question_flag=True, ddtype=self.ddtype)
        value = submission_list.order_formatted_row(question_field.code, answers)
        expected = ['answer']
        self.assertEqual(expected, value)

    def test_should_split_fields_according_to_question_code_for_geocode_fields(self):
        submission_list = self.create_submission_list_instance()
        answers = {'GPS': ('lat', 'long'), 'other_value': 'other_value'}
        question_field = GeoCodeField(label="What is your gps?", code="GPS", name="What is your gps?",
            ddtype=self.ddtype)
        value = submission_list.order_formatted_row(question_field.code, answers)
        expected = ['lat', 'long']
        self.assertEqual(expected, value)

    def test_should_return_blank_if_answer_is_not_present(self):
        submission_list = self.create_submission_list_instance()
        answers = {'other_value': 'other_value', 'some_value': 'some_value'}
        question_field = TextField(label="What is associated entity?", code="EID", name="What is associated entity?",
            entity_question_flag=True, ddtype=self.ddtype)
        value = submission_list.order_formatted_row(question_field.code, answers)
        expected = ['--']
        self.assertEqual(expected, value)

    def test_should_return_blank_if_answer_is_not_present_irrespective_of_case(self):
        submission_list = self.create_submission_list_instance()
        answers = {'EID': 'other_value', 'some_value': 'some_value'}
        question_field = TextField(label="What is associated entity?", code="eid", name="What is associated entity?",
            entity_question_flag=True, ddtype=self.ddtype)
        value = submission_list.order_formatted_row(question_field.code, answers)
        expected = ['other_value']
        self.assertEqual(expected, value)

    def test_reporting_date_is_of_date_type(self):
        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            with patch(
                "datawinners.project.survey_response_data.SurveyResponseData._get_survey_response_details") as get_test_data:
                get_test_data.return_value = 'data_sender', '02.2013', "hospital", 'Apr. 15, 2013, 12:11 PM'
                get_submissions.return_value = []
                form_model = Mock(spec=FormModel)
                form_model.event_time_question.date_format = 'mm.yyyy'
                form_model.event_time_question.code = 'RP'
                form_model.get_field_by_code_and_rev.return_value = DateField(name='RP', code='RP',
                    label='RP', date_format='mm.yyyy', ddtype=Mock())
                analyzer = AnalysisForExcel(form_model, self.manager, self.org_id, [])
                filtered_submissions = Mock(spec=SurveyResponse)
                data_sender, rp, subject, submission_date = analyzer.get_survey_response_details_for_excel(
                    filtered_submissions)
                self.assertEqual(ExcelDate(datetime.strptime('02.2013', '%m.%Y'), 'mm.yyyy'), rp)
                self.assertEqual(
                    ExcelDate(datetime.strptime('Apr. 15, 2013, 12:11 PM', SUBMISSION_DATE_FORMAT_FOR_SUBMISSION),
                        'submission_date'), submission_date)

    def test_reporting_date_is_None_if_there_is_no_reporting_date_type(self):
        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            with patch(
                "datawinners.project.survey_response_data.SurveyResponseData._get_survey_response_details") as get_test_data:
                get_test_data.return_value = 'data_sender', None, "hospital", 'Apr. 15, 2013, 12:11 PM'
                get_submissions.return_value = []
                form_model = Mock(spec=FormModel)
                form_model.event_time_question.date_format = 'mm.yyyy'
                form_model.event_time_question.code = 'RP'
                form_model.get_field_by_code_and_rev.return_value = DateField(name='RP', code='RP',
                    label='RP', date_format='mm.yyyy', ddtype=Mock())
                analyzer = AnalysisForExcel(form_model, self.manager, self.org_id, [])
                filtered_submissions = Mock(spec=SurveyResponse)
                data_sender, rp, subject, submission_date = analyzer.get_survey_response_details_for_excel(
                    filtered_submissions)
                self.assertEqual(None, rp)
                expected_date = ExcelDate(
                    datetime.strptime('Apr. 15, 2013, 12:11 PM', SUBMISSION_DATE_FORMAT_FOR_SUBMISSION),
                    'submission_date')
                self.assertEqual(expected_date, submission_date)

    def test_survey_response_data_is_returned_with_wrong_reporting_date(self):
        filters = {}
        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            data = {"eid": "cli14", "RD": "55.55.2012", "SY": "A2bCZ", "BG": "D"}
            valid_submission = SurveyResponse(self.manager,
                transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                form_code=self.form_model.form_code, values=data)
            get_submissions.return_value = [valid_submission]
            response_data = SurveyResponseList(self.form_model, self.manager, self.org_id, None, filters, None)
            data_sender, rp, subject, submission_date = response_data._get_survey_response_details(
                response_data.filtered_survey_responses[0])
            self.assertEqual("55.55.2012", rp)

    def test_survey_response_submitted_on_date_is_used_for_showing_submission_date(self):
        filters = {}
        with patch(
            "datawinners.project.survey_response_data.SurveyResponseData._get_survey_responses_by_status") as get_submissions:
            data = {"eid": "cli14", "RD": "01.03.2012", "SY": "A2bCZ", "BG": "D"}
            valid_submission = SurveyResponse(self.manager,
                transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                form_code=self.form_model.form_code, values=data)
            valid_submission._doc.created = datetime.strptime('Apr. 12, 2013, 09:27 AM',
                SUBMISSION_DATE_FORMAT_FOR_SUBMISSION)
            valid_submission._doc.submitted_on = datetime.strptime('Apr. 12, 2013, 09:30 AM',
                SUBMISSION_DATE_FORMAT_FOR_SUBMISSION)
            get_submissions.return_value = [valid_submission]
            response_data = SurveyResponseList(self.form_model, self.manager, self.org_id, None, filters, None)
            data_sender, rp, subject, submission_date = response_data._get_survey_response_details(
                response_data.filtered_survey_responses[0])
            self.assertEqual('Apr. 12, 2013, 09:30 AM', submission_date)

