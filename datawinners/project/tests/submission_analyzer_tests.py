## encoding=utf-8
#from datetime import datetime
#from mangrove.transport import Request
#from mangrove.form_model.field import TextField, SelectField, DateField, field_attributes, GeoCodeField, IntegerField
#from mangrove.form_model.form_model import  MOBILE_NUMBER_FIELD, NAME_FIELD
#from mangrove.transport.facade import TransportInfo
#from mangrove.transport.player.player import WebPlayer
#from mangrove.transport.domain.submission import Submission
#from mangrove.utils.entity_builder import EntityBuilder
#from mangrove.utils.form_model_builder import FormModelBuilder, create_default_ddtype
#from mangrove.utils.test_utils.mangrove_test_case import MangroveTestCase
#from project.helper import SUBMISSION_DATE_FORMAT_FOR_SUBMISSION_LOG, NOT_AVAILABLE
#from project.submission_analyzer import SubmissionAnalyzer
#from project.submission_router import successful_submissions
#from project.tests.form_model_generator import FormModelGenerator
#
#today = datetime.utcnow().strftime("%d.%m.%Y")
#
#class SubmissionAnalyzerTest(MangroveTestCase):
#    def setUp(self):
#        super(SubmissionAnalyzerTest, self).setUp()
#        self.org_id = 'SLX364903'
#        self._prepare_subjects()
#
#        self.transport = TransportInfo(transport="web", source="1234", destination="5678")
#        self.form_model_generator = FormModelGenerator(self.manager)
#        self.form_model = self.form_model_generator.form_model()
#
#    def test_should_ignore_not_existed_option(self):
#        data = {"eid": "cli14", "RD": "01.01.2012", "SY": "A2bCZ", "BG": "D"}
#        analyzer = self._prepare_analyzer_with_one_submission(self.form_model, data)
#        try:
#            statistics = analyzer.get_analysis_statistics()
#        except Exception:
#            self.assertTrue(False)
#
#        q1 = ["Zhat are symptoms?", field_attributes.MULTISELECT_FIELD, 1,[
#            ["Dry cough", 1],
#            ["Pneumonia", 1],
#            ["Rapid weight loss", 1],
#            ["Memory loss", 0],
#            ["Neurological disorders ", 0]]
#        ]
#        q2 = ["What is your blood group?", field_attributes.SELECT_FIELD, 1,[["B+", 1], ["AB", 0], ["O+", 0], ["O-", 0]]]
#        expected = [q1, q2]
#        self.assertEqual(expected, statistics)
#
#    def _prepare_subjects(self):
#        self.ddtype = create_default_ddtype(self.manager)
#        EntityBuilder(self.manager, ['clinic'], 'cli14').add_data([(NAME_FIELD, "Clinic-One", self.ddtype)]).build()
#        EntityBuilder(self.manager, ['clinic'], 'cli15').add_data([(NAME_FIELD, "Clinic-Two", self.ddtype)]).build()
#        EntityBuilder(self.manager, ['clinic'], 'cid001').add_data([(MOBILE_NUMBER_FIELD, "919970059125", self.ddtype), (NAME_FIELD, "Ritesh", self.ddtype)]).build()
#
#
#    def test_should_get_option_values_for_questions_case_insensitively(self):
#        data = {"eid": "cli14", "RD": "01.01.2012", "SY": "A2bC", "BG": "D"}
#        analyzer = self._prepare_analyzer_with_one_submission(self.form_model, data)
#
#        raw_field_values = analyzer.get_raw_values()
#        expected = [[self.submission_id, ('Clinic-One', 'cli14'),  '01.01.2012', ('Tester Pune', 'admin', 'tester150411@gmail.com'), ['Rapid weight loss', 'Dry cough', 'Pneumonia'], ['B+']]]
#        submission_date = self.get_submission_date_in_old_format(raw_field_values[0].pop(3))
#        self.assertEqual(today, submission_date)
#        self.assertEqual(expected, raw_field_values)
#
#    def test_should_get_real_answer_for_select_question(self):
#        answers = {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"}
#        submission_analyzer = self._prepare_analyzer_with_one_submission(self.form_model, answers)
#        raw_field_values = submission_analyzer.get_raw_values()
#        expected = [[self.submission_id, ('Clinic-One', 'cli14'), '01.01.2012', (u'Tester Pune', 'admin', u'tester150411@gmail.com'), ['Rapid weight loss', 'Dry cough', 'Pneumonia'], ['B+']]]
#        submission_date = self.get_submission_date_in_old_format(raw_field_values[0].pop(3))
#
#        self.assertEqual(today, submission_date)
#        self.assertEqual(expected, raw_field_values)
#
#    def test_should_get_leading_part_for_non_summary_project(self):
#        analyzer = self._prepare_analyzer_with_one_submission(self.form_model, {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"})
#
#        expected = [[self.submission_id, ('Clinic-One', 'cli14'), '01.01.2012', ('Tester Pune', 'admin', 'tester150411@gmail.com')]]
#        result = analyzer._get_leading_part()
#        submission_date = self.get_submission_date_in_old_format(result[0].pop(3))
#        self.assertEqual(today, submission_date)
#        self.assertEqual(expected, result)
#
#    def test_should_get_leading_part_for_summary_project(self):
#        analyzer = self._prepare_analyzer_with_one_submission(self.form_model_generator.summary_form_model_without_rp(), {"eid": "rep01", "SY": "a2bc", "BG": "d"})
#        leading_part = analyzer._get_leading_part()
#        expected = [[self.submission_id, ('Tester Pune', 'admin', 'tester150411@gmail.com')]]
#        submission_date = self.get_submission_date_in_old_format(leading_part[0].pop(1))
#        self.assertEqual(today, submission_date)
#        self.assertEqual(expected, leading_part)
#
#    def test_should_get_raw_field_values(self):
#        analyzer = self._prepare_analyzer_with_one_submission(self.form_model, {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"})
#
#        raw_field_values = analyzer.get_raw_values()
#        expected = [[self.submission_id, ('Clinic-One', 'cli14'),  '01.01.2012', ('Tester Pune', 'admin', 'tester150411@gmail.com'), ['Rapid weight loss', 'Dry cough', 'Pneumonia'], ['B+']]]
#        submission_date = self.get_submission_date_in_old_format(raw_field_values[0].pop(3))
#        self.assertEqual(today, submission_date)
#        self.assertEqual(expected, raw_field_values)
#
#    def test_should_get_raw_field_values_with_status_for_all_submissions(self):
#        analyzer = self._prepare_analyzer_with_one_submission(self.form_model, {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"}, is_for_submission_page=True)
#        submission_date = datetime.utcnow().strftime(SUBMISSION_DATE_FORMAT_FOR_SUBMISSION_LOG)
#        raw_field_values = analyzer.get_raw_values()
#        expected = [[self.submission_id, (u'Tester Pune', 'admin', u'tester150411@gmail.com'), submission_date, 'Error', '-', ('Clinic-One', 'cli14'), '01.01.2012', ['Rapid weight loss', 'Dry cough', 'Pneumonia'], ['B+']]]
#        self.assertEqual(expected, raw_field_values)
#
#    def test_should_get_raw_field_values_filtered_by_keyword(self):
#        data = [{"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"},
#              {"eid": "cli15", "RD": "02.02.2012", "SY": "c", "BG": "d"}]
#        analyzer = self._prepare_analyzer(self.form_model, data, "Rapid")
#
#        result = analyzer.get_raw_values()
#        self.assertEqual(1, len(result))
#        self.assertIn('Rapid', repr(result))
#
#    def test_should_get_subject_list(self):
#        data = [
#            {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"},
#            {"eid": "cli15", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"},
#            {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"}
#        ]
#        analyzer = self._prepare_analyzer(self.form_model, data)
#        subject_list = analyzer.get_subjects()
#        expected = [('Clinic-One', u'cli14'), ('Clinic-Two', u'cli15')]
#        self.assertEqual(expected, subject_list)
#
#    def test_should_get_subject_list_for_submission_log_page(self):
#        data = [
#            {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"},
#            {"eid": "cli15", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"},
#            {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"},
#            {"1": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"}
#        ]
#        analyzer = self._prepare_analyzer(self.form_model, data, is_for_submission_page=True)
#        subject_list = analyzer.get_subjects()
#        expected = [('Clinic-One', u'cli14'), ('Clinic-Two', u'cli15'), (NOT_AVAILABLE, str(None))]
#        self.assertEqual(expected, subject_list)
#
#    def test_should_get_data_sender_list(self):
#        analyzer = self._prepare_analyzer_with_one_submission(self.form_model,
#            {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"})
#        data_sender_list = analyzer.get_data_senders()
#        expected = [('Tester Pune', 'admin', 'tester150411@gmail.com')]
#        self.assertEqual(expected, data_sender_list)
#
#    def test_should_get_statistic_result(self):
#        """
#            Function to test getting statistic result.
#            question name ordered by field
#            options ordered by count(desc),option(alphabetic)
#            total = submission count of this question
#        """
#        data = [{"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"},
#              {"eid": "cli14", "RD": "01.01.2012", "BG": "c"}
#             ]
#        analyzer = self._prepare_analyzer(self.form_model, data)
#        statistics = analyzer.get_analysis_statistics()
#
#        q1 = ["Zhat are symptoms?", field_attributes.MULTISELECT_FIELD, 1,[
#                                                                            ["Dry cough", 1],
#                                                                            ["Pneumonia", 1],
#                                                                            ["Rapid weight loss", 1],
#                                                                            ["Memory loss", 0],
#                                                                            ["Neurological disorders ", 0]]
#                                                                           ]
#        q2 = ["What is your blood group?", field_attributes.SELECT_FIELD, 2,[["AB", 1],["B+", 1], ["O+", 0], ["O-", 0]]]
#        expected = [q1, q2]
#        self.assertEqual(expected, statistics)
#
#    def test_should_get_statistic_result_after_answer_type_changed_from_word_to_mc(self):
#        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associatéd entity?",entity_question_flag=True, ddtype=self.ddtype)
#        blood_type_field = TextField(label="What is your blood group?", code="BG", name="What is your blood group?", ddtype=self.ddtype)
#
#        form_model = FormModelBuilder(self.manager, ['clinic'], form_code='cli001').add_fields(eid_field, blood_type_field).build()
#        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'BG': 'unknown'})
#
#        blood_type_field = SelectField(label="What is your blood group?", code="BG", name="What is your blood group?", options=[("O+", "a"), ("O-", "b"), ("AB", "c"), ("B+", "d")], single_select_flag=False, ddtype=self.ddtype)
#        self._edit_fields(form_model, blood_type_field)
#        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'BG': 'ab'})
#
#        submissions = successful_submissions(self.manager, form_model.form_code)
#        analyzer = SubmissionAnalyzer(form_model, self.manager, self.org_id, submissions)
#        statistics = analyzer.get_analysis_statistics()
#
#        expected = [["What is your blood group?", field_attributes.MULTISELECT_FIELD, 2, [["O+", 1], ["O-", 1], ['unknown', 1], ["AB", 0], ["B+", 0]]]]
#        self.assertEqual(expected, statistics)
#
#    def test_should_get_statistic_result_after_option_value_changed(self):
#        """
#            Function to test getting statistic result of submissions after option value changed.
#            question name ordered by field
#            options ordered by count(desc),option(alphabetic)
#            total = submission count of this question
#        """
#        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associatéd entity?",entity_question_flag=True, ddtype=self.ddtype)
#        blood_type_field = SelectField(label="What is your blood group?", code="BG", name="What is your blood group?",
#            options=[("Type 1", "a"),("Type 2", "b")], single_select_flag=True, ddtype=self.ddtype)
#
#        form_model = FormModelBuilder(self.manager, ['clinic'], form_code='cli001').add_fields(eid_field, blood_type_field).build()
#
#        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'BG': 'a'})
#
#        blood_type_field = SelectField(label="What is your blood group?", code="BG", name="What is your blood group?", options=[("O+", "a"), ("O-", "b"), ("AB", "c"), ("B+", "d")], single_select_flag=True, ddtype=self.ddtype)
#        self._edit_fields(form_model, blood_type_field)
#        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'BG': 'a'})
#
#        submissions = successful_submissions(self.manager, form_model.form_code)
#        analyzer = SubmissionAnalyzer(form_model, self.manager, self.org_id, submissions)
#        statistics = analyzer.get_analysis_statistics()
#
#        expected = [["What is your blood group?", field_attributes.SELECT_FIELD, 2, [["O+", 1], ['Type 1', 1], ["AB", 0], ["B+", 0], ["O-", 0]]]]
#        self.assertEqual(expected, statistics)
#
#    def test_should_sort_by_submission_date_for_subject_project_with_rp(self):
#        data = {"eid": "cli14", "RD": "01.01.2012", "SY": "A2bCZ", "BG": "D"}
#        analyzer = self._prepare_analyzer_with_one_submission(self.form_model, data)
#        default_sort_order = analyzer.get_default_sort_order()
#        self.assertEqual([[3, 'desc']], default_sort_order)
#
#    def test_should_sort_by_submission_date_for_subject_project_without_rp(self):
#        self.form_model = self.form_model_generator.subject_form_model_without_rp()
#        data = {"eid": "cli14", "RD": "01.01.2012", "SY": "A2bCZ", "BG": "D"}
#        analyzer = self._prepare_analyzer_with_one_submission(self.form_model, data)
#        default_sort_order = analyzer.get_default_sort_order()
#        self.assertEqual([[2, 'desc']], default_sort_order)
#
#    def test_should_sort_submission_date_for_summary_project_with_rp(self):
#        self.form_model = self.form_model_generator.summary_form_model_with_rp()
#        data = {"eid": "cli14", "RD": "01.01.2012", "SY": "A2bCZ", "BG": "D"}
#        analyzer = self._prepare_analyzer_with_one_submission(self.form_model, data)
#        default_sort_order = analyzer.get_default_sort_order()
#        self.assertEqual([[2, 'desc']], default_sort_order)
#
#    def test_should_sort_by_submission_date_for_summary_project_without_rp(self):
#        self.form_model = self.form_model_generator.summary_form_model_without_rp()
#        data = {"eid": "cli14", "RD": "01.01.2012", "SY": "A2bCZ", "BG": "D"}
#        analyzer = self._prepare_analyzer_with_one_submission(self.form_model, data)
#        default_sort_order = analyzer.get_default_sort_order()
#        self.assertEqual([[1, 'desc']], default_sort_order)
#
#    def submit_data(self, post_data):
#        WebPlayer(self.manager).accept(Request(message=post_data, transportInfo=self.transport))
#
#    def test_should_get_old_answer_for_submissions_which_is_submitted_before_MC_changed_to_other(self):
#        """
#        Function to test get old answer for submissions which is submitted before answer type changed from multiple choice/single choice to other type(word, number, date, GPS)
#        """
#        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associatéd entity?",entity_question_flag=True, ddtype=self.ddtype)
#        rp_field = DateField(label="Report date", code="RD", name="What is réporting date?",date_format="dd.mm.yyyy", event_time_field_flag=True, ddtype=self.ddtype)
#        symptoms_field = SelectField(label="Zhat are symptoms?", code="SY", name="Zhat are symptoms?",
#            options=[("Rapid weight loss", "a"), ("Dry cough", "b"), ("Pneumonia", "c"),
#                     ("Memory loss", "d"), ("Neurological disorders ", "e")], single_select_flag=False, ddtype=self.ddtype)
#        blood_type_field = SelectField(label="What is your blood group?", code="BG", name="What is your blood group?",
#            options=[("O+", "a"), ("O-", "b"), ("AB", "c"), ("B+", "d")], single_select_flag=True, ddtype=self.ddtype)
#
#        form_model = FormModelBuilder(self.manager, ['clinic'], form_code='cli001').add_fields(eid_field, rp_field,symptoms_field, blood_type_field).build()
#
#        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.12.2012', 'SY': 'ab', 'BG': 'b'})
#        self._edit_fields(form_model, IntegerField(label="Zhat are symptoms?", code="SY", name="Zhat are symptoms?", ddtype=self.ddtype))
#
#        submissions = successful_submissions(self.manager, form_model.form_code)
#        analyzer = SubmissionAnalyzer(form_model, self.manager, self.org_id, submissions)
#        values = analyzer.get_raw_values()
#
#        self.assertEqual([['Rapid weight loss','Dry cough'], ['O-']], values[0][5:])
#
#    def test_should_get_old_answer_for_submissions_which_is_submitted_before_other_changed_to_MC(self):
#        """
#        Function to test get old answer for submissions which is submitted before answer type changed from other type(word, number, date, GPS) to multiple choice/single choice
#        """
#        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associatéd entity?",entity_question_flag=True, ddtype=self.ddtype)
#        rp_field = DateField(label="Report date", code="RD", name="What is réporting date?",date_format="dd.mm.yyyy", event_time_field_flag=True, ddtype=self.ddtype)
#        symptoms_field = TextField(label="Zhat are symptoms?", code="SY", name="Zhat are symptoms?", ddtype=self.ddtype)
#        blood_type_field = SelectField(label="What is your blood group?", code="BG", name="What is your blood group?",
#            options=[("O+", "a"), ("O-", "b"), ("AB", "c"), ("B+", "d")], single_select_flag=True, ddtype=self.ddtype)
#
#        form_model = FormModelBuilder(self.manager, ['clinic'], form_code='cli001').add_fields(eid_field, rp_field,symptoms_field, blood_type_field).build()
#        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.12.2012', 'SY': 'Fever', 'BG': 'b'})
#
#        symptoms_field = SelectField(label="Zhat are symptoms?", code="SY", name="Zhat are symptoms?",
#            options=[("Rapid weight loss", "a"), ("Dry cough", "b"), ("Pneumonia", "c"),
#                     ("Memory loss", "d"), ("Neurological disorders ", "e")], single_select_flag=False, ddtype=self.ddtype)
#        self._edit_fields(form_model, symptoms_field)
#        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.12.2012', 'SY': 'ab', 'BG': 'b'})
#
#        submissions = successful_submissions(self.manager, form_model.form_code)
#        analyzer = SubmissionAnalyzer(form_model, self.manager, self.org_id, submissions)
#        values = analyzer.get_raw_values()
#
#        self.assertEqual([['Rapid weight loss','Dry cough'], ['O-']], values[0][5:])
#        self.assertEqual(['Fever', ['O-']], values[1][5:])
#
#    def test_should_get_old_answer_for_submissions_which_is_submitted_before_other_changed_to_other(self):
#        """
#        Function to test get old answer for submissions which is submitted before answer type changed from other type(word, number, date, GPS) to other type
#        """
#        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associatéd entity?",
#            entity_question_flag=True, ddtype=self.ddtype)
#        rp_field = DateField(label="Report date", code="RD", name="What is réporting date?", date_format="dd.mm.yyyy",
#            event_time_field_flag=True, ddtype=self.ddtype)
#        symptoms_field = TextField(label="Zhat are symptoms?", code="SY", name="Zhat are symptoms?", ddtype=self.ddtype)
#        gps = TextField(label="What is your blood group?", code="GPS", name="What is your gps?", ddtype=self.ddtype)
#        national_day_field = TextField(label="national day?", code="ND", name="national day", ddtype=self.ddtype)
#        form_model = FormModelBuilder(self.manager, ['clinic'], form_code='cli001').add_fields(eid_field, rp_field,
#            symptoms_field, gps, national_day_field).build()
#
#        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.12.2012', 'SY': 'Fever', 'GPS': 'NewYork', "ND":"oct 1"})
#
#        gps = GeoCodeField(label="What is your blood group?", code="GPS", name="What is your gps?", ddtype=self.ddtype)
#        symptoms_field = IntegerField(label="Zhat are symptoms?", code="SY", name="Zhat are symptoms?", ddtype=self.ddtype)
#        national_day_field = DateField(label="national day?", code="ND", name="national day", ddtype=self.ddtype, date_format="dd.mm.yyyy")
#
#        self._edit_fields(form_model, gps, national_day_field, symptoms_field)
#        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.12.2012', 'SY': '100', 'GPS': '1,1', "ND":"01.10.2012"})
#
#        submissions = successful_submissions(self.manager, form_model.form_code)
#        analyzer = SubmissionAnalyzer(form_model, self.manager, self.org_id, submissions)
#        values = analyzer.get_raw_values()
#
#        self.assertEqual(['100', '1,1', '01.10.2012'], values[0][5:])
#        self.assertEqual(['Fever', 'NewYork', 'oct 1'], values[1][5:])
#
#    def test_should_show_previous_submissions_in_old_format_after_change_date_format(self):
#        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associatéd entity?",
#            entity_question_flag=True, ddtype=self.ddtype)
#        rp_field = DateField(label="Report date", code="RD", name="What is réporting date?", date_format="dd.mm.yyyy",
#            event_time_field_flag=True, ddtype=self.ddtype)
#
#        form_model = FormModelBuilder(self.manager, ['clinic'], form_code='cli001').add_fields(eid_field, rp_field).build()
#
#        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.12.2012'})
#
#        rp_field = DateField(label="Report date", code="RD", name="What is réporting date?", date_format="mm.yyyy",event_time_field_flag=True, ddtype=self.ddtype)
#        self._edit_fields(form_model, rp_field)
#        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'RD': '08.2012'})
#
#        rp_field = DateField(label="Report date", code="RD", name="What is réporting date?", date_format="mm.dd.yyyy",event_time_field_flag=True, ddtype=self.ddtype)
#        self._edit_fields(form_model, rp_field)
#        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.24.2012'})
#
#        submissions = successful_submissions(self.manager, form_model.form_code)
#        analyzer = SubmissionAnalyzer(form_model, self.manager, self.org_id, submissions)
#        values = analyzer.get_raw_values()
#        reporting_periods = map(lambda value: value[2], values)
#
#        self.assertIn('08.2012', reporting_periods)
#        self.assertIn('12.12.2012', reporting_periods)
#        self.assertIn('12.24.2012', reporting_periods)
#
#    def test_should_should_get_fields_values_after_question_count_changed(self):
#        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associatéd entity?",
#            entity_question_flag=True, ddtype=self.ddtype)
#        rp_field = DateField(label="Report date", code="RD", name="What is réporting date?", date_format="dd.mm.yyyy",
#            event_time_field_flag=True, ddtype=self.ddtype)
#        symptoms_field = TextField(label="Zhat are symptoms?", code="SY", name="Zhat are symptoms?", ddtype=self.ddtype)
#        gps = TextField(label="What is your blood group?", code="GPS", name="What is your gps?", ddtype=self.ddtype)
#        form_model = FormModelBuilder(self.manager, ['clinic'], form_code='cli001').add_fields(eid_field, rp_field,
#            symptoms_field, gps).build()
#
#        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.12.2012', 'SY': 'Fever', 'GPS': 'NewYork'})
#
#        form_model.create_snapshot()
#        form_model.delete_field("SY")
#        form_model.save()
#
#        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.12.2012', 'GPS': '1,1'})
#
#        submissions = successful_submissions(self.manager, form_model.form_code)
#        analyzer = SubmissionAnalyzer(form_model, self.manager, self.org_id, submissions)
#        values = analyzer.get_raw_values()
#
#        self.assertEqual(['1,1'], values[0][5:])
#        self.assertEqual(['NewYork'], values[1][5:])
#
#    def _prepare_analyzer_with_one_submission(self, form_model, values, is_for_submission_page=False):
#        submission = Submission(self.manager,
#            transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
#            form_code=form_model.form_code,
#            values=values)
#        self.submission_id = submission.id
#
#        return SubmissionAnalyzer(form_model, self.manager, self.org_id, [submission], is_for_submission_page=is_for_submission_page)
#
#    def _prepare_analyzer(self, form_model, values_list, keywords=None, is_for_submission_page=False):
#        submissions = []
#        for values in values_list:
#            submission = Submission(self.manager,
#                transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
#                form_code=form_model.form_code,
#                values=values)
#            submissions.append(submission)
#
#        return SubmissionAnalyzer(form_model, self.manager, self.org_id, submissions, keywords, is_for_submission_page=is_for_submission_page)
#
#    def _edit_fields(self, form_model, *updated_fields):
#        fields = []
#        for field in form_model.fields:
#            need_update = False
#            for update in updated_fields:
#                if update.code == field.code:
#                    need_update = True
#                    fields.append(update)
#            if not need_update:
#                fields.append(field)
#
#        form_model.create_snapshot()
#        form_model.delete_all_fields()
#        [form_model.add_field(each) for each in fields]
#        form_model.save()
#
#    def get_submission_date_in_old_format(self, submission_date):
#        submission_date = datetime.strptime(submission_date, SUBMISSION_DATE_FORMAT_FOR_SUBMISSION_LOG)
#        submission_date = submission_date.strftime("%d.%m.%Y")
#        return submission_date