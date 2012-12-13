# encoding=utf-8
from datetime import datetime
from mangrove.transport import Request
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import Entity
from mangrove.form_model.field import TextField, SelectField, DateField, field_attributes, GeoCodeField, IntegerField
from mangrove.form_model.form_model import  MOBILE_NUMBER_FIELD, NAME_FIELD
from mangrove.transport.facade import TransportInfo
from mangrove.transport.player.player import WebPlayer
from mangrove.transport.submissions import Submission, successful_submissions
from mock import Mock, patch
from mangrove.utils.entity_builder import EntityBuilder
from mangrove.utils.form_model_builder import FormModelBuilder, create_default_ddtype
from mangrove.utils.test_utils.mangrove_test_case import MangroveTestCase
from project.submission_analyzer import SubmissionAnalyzer
from project.tests.form_model_generator import FormModelGenerator

today = datetime.utcnow().strftime("%d.%m.%Y")

class SubmissionAnalyzerTest(MangroveTestCase):
    def setUp(self):
        super(SubmissionAnalyzerTest, self).setUp()
        self.mocked_dbm = Mock(spec=DatabaseManager)
        self.user = Mock()
        self.transport = TransportInfo(transport="web", source="1234", destination="5678")
        self.form_model_generator = FormModelGenerator(self.manager)
        self.form_model = self.form_model_generator.form_model()

    def test_should_ignore_not_existed_option(self):
        data = {"eid": "cli14", "RD": "01.01.2012", "SY": "A2bCZ", "BG": "D"}
        analyzer = self._prepare_analyzer_with_one_submission(self.form_model, data)

        with patch("project.submission_analyzer.SubmissionAnalyzer._get_leading_part") as _get_leading_part:
            _get_leading_part.return_value = [[('Clinic-2', 'cli14'),  '01.01.2012', today, ('name', 'id', 'from')]]
            analyzer._init_raw_values()
            try:
                statistics = analyzer.get_analysis_statistics()
            except Exception:
                self.assertTrue(False)

            q1 = ["Zhat are symptoms?", field_attributes.MULTISELECT_FIELD, 1,[
                ["Dry cough", 1],
                ["Pneumonia", 1],
                ["Rapid weight loss", 1],
                ["Memory loss", 0],
                ["Neurological disorders ", 0]]
            ]
            q2 = ["What is your blood group?", field_attributes.SELECT_FIELD, 1,[["B+", 1], ["AB", 0], ["O+", 0], ["O-", 0]]]
            expected = [q1, q2]
            self.assertEqual(expected, statistics)

    def test_should_get_option_values_for_questions_case_insensitively(self):
        data = {"eid": "cli14", "RD": "01.01.2012", "SY": "A2bC", "BG": "D"}
        analyzer = self._prepare_analyzer_with_one_submission(self.form_model, data)

        with patch("project.submission_analyzer.get_data_sender") as get_data_sender, patch(
            "project.submission_analyzer.get_by_short_code") as get_by_short_code, patch(
            "project.submission_analyzer.SubmissionAnalyzer._get_leading_part") as _get_leading_part:
            get_data_sender.return_value = ('name', 'id', 'from')
            get_by_short_code.return_value = self._prepare_clinic_entity()
            analyzer._get_leading_part.return_value = [[('Clinic-One', 'cli14'),  '01.01.2012', today, ('name', 'id', 'from')]]
            analyzer._init_raw_values()
            raw_field_values = analyzer.get_raw_values()
            expected = [[('Clinic-One', 'cli14'),  '01.01.2012', today, ('name', 'id', 'from'), ['Rapid weight loss', 'Dry cough', 'Pneumonia'], ['B+']]]
            self.assertEqual(expected, raw_field_values)

    def test_should_get_real_answer_for_select_question(self):
        row = (None, {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"})
        expected = {"eid": "cli14","RD": "01.01.2012", "SY": ['Rapid weight loss', 'Dry cough', 'Pneumonia'], "BG": ['B+']}
        self._prepare_analyzer_with_one_submission(self.form_model, row)._replace_option_with_real_answer_value(row)
        self.assertEqual(expected, row[-1])

    def test_should_get_leading_part_for_non_summary_project(self):
        analyzer = self._prepare_analyzer_with_one_submission(self.form_model, {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"})

        with patch("project.submission_analyzer.get_data_sender") as get_data_sender, patch(
            "project.submission_analyzer.get_by_short_code") as get_by_short_code:
            get_data_sender.return_value = ('name', 'id', 'from')
            get_by_short_code.return_value = self._prepare_clinic_entity()
            leading_part = analyzer._get_leading_part()
            expected = [[('Clinic-One', 'cli14'), '01.01.2012', today, ('name', 'id', 'from')]]
            self.assertEqual(expected, leading_part)

    def test_should_get_leading_part_for_summary_project(self):
        analyzer = self._prepare_analyzer_with_one_submission(self.form_model_generator.summary_form_model_without_rp(), {"eid": "rep01", "SY": "a2bc", "BG": "d"})

        with patch("project.submission_analyzer.get_data_sender") as get_data_sender, patch(
            "project.submission_analyzer.get_by_short_code") as get_by_short_code:
            get_data_sender.return_value = ('name', 'id', 'from')
            get_by_short_code.return_value = self._prepare_clinic_entity()
            leading_part = analyzer._get_leading_part()
            expected = [[today, ('name', 'id', 'from')]]
            self.assertEqual(expected, leading_part)

    def test_should_get_raw_field_values(self):
        analyzer = self._prepare_analyzer_with_one_submission(self.form_model, {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"})

        with patch("project.submission_analyzer.get_data_sender") as get_data_sender, patch(
            "project.submission_analyzer.get_by_short_code") as get_by_short_code:
            get_data_sender.return_value = ('name', 'id', 'from')
            get_by_short_code.return_value = self._prepare_clinic_entity()
            analyzer._init_raw_values()
            raw_field_values = analyzer.get_raw_values()
            expected = [[('Clinic-One', 'cli14'),  '01.01.2012', today, ('name', 'id', 'from'), ['Rapid weight loss', 'Dry cough', 'Pneumonia'], ['B+']]]
            self.assertEqual(expected, raw_field_values)

    def test_should_get_raw_field_values_with_status_for_all_submissions(self):
        analyzer = self._prepare_analyzer_with_one_submission(self.form_model, {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"}, with_status=True)

        with patch("project.submission_analyzer.get_data_sender") as get_data_sender, patch(
            "project.submission_analyzer.get_by_short_code") as get_by_short_code:
            get_data_sender.return_value = ('name', 'id', 'from')
            get_by_short_code.return_value = self._prepare_clinic_entity()
            analyzer._init_raw_values()
            raw_field_values = analyzer.get_raw_values()
            expected = [[('Clinic-One', 'cli14'),  '01.01.2012', today, u'Error', ('name', 'id', 'from'), ['Rapid weight loss', 'Dry cough', 'Pneumonia'], ['B+']]]
            self.assertEqual(expected, raw_field_values)

    def test_should_get_raw_field_values_filtered_by_keyword(self):
        data = [{"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"},
              {"eid": "cli15", "RD": "02.02.2012", "SY": "c", "BG": "d"}]
        analyzer = self._prepare_analyzer(self.form_model, data, "Rapid")

        with patch("project.submission_analyzer.get_data_sender") as get_data_sender, patch(
            "project.submission_analyzer.get_by_short_code") as get_by_short_code, patch(
             "project.submission_analyzer.SubmissionAnalyzer._get_leading_part") as _get_leading_part , patch(
            "project.submission_analyzer.SubmissionAnalyzer._get_field_values") as _get_field_values:
            get_data_sender.return_value = ('name', 'id', 'from')
            get_by_short_code.return_value = self._prepare_clinic_entity()
            analyzer._get_leading_part.return_value = [[('Clinic-One', 'cli14'),  '01.01.2012', today, ('name', 'id', 'from')],
                                     [('Clinic-Two', 'cli15'),  '02.02.2012', today, ('name_2', 'id_2', 'from_2')]]
            analyzer._get_field_values.return_value = [['cli14',['Rapid weight loss', 'Dry cough', 'Pneumonia'], ['B+']],
                                    ['cli15',['Pneumonia'], ['B+']]]
            analyzer._init_raw_values()
            raw_field_values = analyzer.get_raw_values()
            expected = [[('Clinic-One', 'cli14'),  '01.01.2012', today, ('name', 'id', 'from'), ['Rapid weight loss', 'Dry cough', 'Pneumonia'], ['B+']]]
            self.assertEqual(expected, raw_field_values)

    def test_should_get_subject_list(self):
        form_model = self.form_model
        analyzer = self._prepare_analyzer_with_one_submission(form_model, {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"})
        analyzer.filtered_leading_part =  [[('Clinic-2', 'cli14'),  '01.01.2012', today, ('name', 'id', 'from')],
                                              [('Clinic-1', 'cli15'),  '01.01.2011', today, ('name_2', 'id_2', 'from_2')],
                                              [('Clinic-1', 'cli15'),  '01.10.2011', today, ('name_3', 'id_3', 'from_3')]]
        subject_list = analyzer.get_subjects()
        expected = [('Clinic-1', 'cli15'), ('Clinic-2', 'cli14')]
        self.assertEqual(expected, subject_list)

    def test_should_get_data_sender_list(self):
        analyzer = self._prepare_analyzer_with_one_submission(self.form_model, {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"})

        analyzer.filtered_leading_part = [[('Clinic-2', 'cli14'),  '01.01.2012', today, ('name_2', 'id_2', 'from_2')],
                                          [('Clinic-1', 'cli15'),  '01.01.2011', today, ('name_1', 'id_1', 'from_1')],
                                          [('Clinic-3', 'cli16'),  '01.10.2011', today, ('name_2', 'id_2', 'from_2')]]

        data_sender_list = analyzer.get_data_senders()
        expected = [('name_1', 'id_1', 'from_1'), ('name_2', 'id_2', 'from_2')]
        self.assertEqual(expected, data_sender_list)

    def test_should_get_statistic_result(self):
        """
            Function to test getting statistic result.
            question name ordered by field
            options ordered by count(desc),option(alphabetic)
            total = submission count of this question
        """
        data = [{"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"},
              {"eid": "cli14", "RD": "01.01.2012", "BG": "c"}
             ]
        analyzer = self._prepare_analyzer(self.form_model, data)

        with patch("project.submission_analyzer.SubmissionAnalyzer._get_leading_part") as _get_leading_part:
            _get_leading_part.return_value = [[('Clinic-2', 'cli14'),  '01.01.2012', today, ('name', 'id', 'from')],
                                     [('Clinic-3', 'cli15'),  '02.02.2012', today, ('name_2', 'id_2', 'from_3')]]
            analyzer._init_raw_values()
            statistics = analyzer.get_analysis_statistics()

            q1 = ["Zhat are symptoms?", field_attributes.MULTISELECT_FIELD, 1,[
                                                                                ["Dry cough", 1],
                                                                                ["Pneumonia", 1],
                                                                                ["Rapid weight loss", 1],
                                                                                ["Memory loss", 0],
                                                                                ["Neurological disorders ", 0]]
                                                                               ]
            q2 = ["What is your blood group?", field_attributes.SELECT_FIELD, 2,[["AB", 1],["B+", 1], ["O+", 0], ["O-", 0]]]
            expected = [q1, q2]
            self.assertEqual(expected, statistics)

    def test_should_get_statistic_result_after_answer_type_changed_from_word_to_mc(self):
        ddtype = create_default_ddtype(self.manager)
        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associatéd entity?",entity_question_flag=True, ddtype=ddtype)
        blood_type_field = TextField(label="What is your blood group?", code="BG", name="What is your blood group?", ddtype=ddtype)

        form_model = FormModelBuilder(self.manager, ['clinic'], form_code='cli001').add_fields(eid_field, blood_type_field).build()
        EntityBuilder(self.manager, ['clinic'], 'cid001').add_data([(MOBILE_NUMBER_FIELD, "919970059125", ddtype), (NAME_FIELD, "Ritesh", ddtype)]).build()

        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'BG': 'unknown'})

        blood_type_field = SelectField(label="What is your blood group?", code="BG", name="What is your blood group?", options=[("O+", "a"), ("O-", "b"), ("AB", "c"), ("B+", "d")], single_select_flag=False, ddtype=ddtype)
        self._edit_fields(form_model, blood_type_field)
        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'BG': 'ab'})

        submissions = successful_submissions(self.manager, form_model.form_code)
        analyzer = SubmissionAnalyzer(form_model, self.manager, self.user, submissions)
        statistics = analyzer.get_analysis_statistics()

        expected = [["What is your blood group?", field_attributes.MULTISELECT_FIELD, 2, [["O+", 1], ["O-", 1], ['unknown', 1], ["AB", 0], ["B+", 0]]]]
        self.assertEqual(expected, statistics)

    def test_should_get_statistic_result_after_option_value_changed(self):
        """
            Function to test getting statistic result of submissions after option value changed.
            question name ordered by field
            options ordered by count(desc),option(alphabetic)
            total = submission count of this question
        """
        ddtype = create_default_ddtype(self.manager)
        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associatéd entity?",entity_question_flag=True, ddtype=ddtype)
        blood_type_field = SelectField(label="What is your blood group?", code="BG", name="What is your blood group?",
            options=[("Type 1", "a"),("Type 2", "b")], single_select_flag=True, ddtype=ddtype)

        form_model = FormModelBuilder(self.manager, ['clinic'], form_code='cli001').add_fields(eid_field, blood_type_field).build()
        EntityBuilder(self.manager, ['clinic'], 'cid001').add_data([(MOBILE_NUMBER_FIELD, "919970059125", ddtype), (NAME_FIELD, "Ritesh", ddtype)]).build()

        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'BG': 'a'})

        blood_type_field = SelectField(label="What is your blood group?", code="BG", name="What is your blood group?", options=[("O+", "a"), ("O-", "b"), ("AB", "c"), ("B+", "d")], single_select_flag=True, ddtype=ddtype)
        self._edit_fields(form_model, blood_type_field)
        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'BG': 'a'})

        submissions = successful_submissions(self.manager, form_model.form_code)
        analyzer = SubmissionAnalyzer(form_model, self.manager, self.user, submissions)
        statistics = analyzer.get_analysis_statistics()

        expected = [["What is your blood group?", field_attributes.SELECT_FIELD, 2, [["O+", 1], ['Type 1', 1], ["AB", 0], ["B+", 0], ["O-", 0]]]]
        self.assertEqual(expected, statistics)

    def test_should_sort_by_rp_and_subject_for_subject_project_with_rp(self):
        analyzer = self._prepare_analyzer_with_one_submission(self.form_model, None)
        default_sort_order = analyzer.get_default_sort_order()
        self.assertEqual([[1, 'desc'],[0, 'asc']], default_sort_order)

    def test_should_sort_by_submission_date_and_subject_for_subject_project_without_rp(self):
        self.form_model = self.form_model_generator.subject_form_model_without_rp()
        analyzer = self._prepare_analyzer_with_one_submission(self.form_model, None)
        default_sort_order = analyzer.get_default_sort_order()
        self.assertEqual([[1, 'desc'],[0, 'asc']], default_sort_order)

    def test_should_sort_by_rp_and_ds_for_summary_project_with_rp(self):
        self.form_model = self.form_model_generator.summary_form_model_with_rp()
        analyzer = self._prepare_analyzer_with_one_submission(self.form_model, None)
        default_sort_order = analyzer.get_default_sort_order()
        self.assertEqual([[0, 'desc'],[2, 'asc']], default_sort_order)

    def test_should_sort_by_submission_date_and_ds_for_summary_project_without_rp(self):
        self.form_model = self.form_model_generator.summary_form_model_without_rp()
        analyzer = self._prepare_analyzer_with_one_submission(self.form_model, None)
        default_sort_order = analyzer.get_default_sort_order()
        self.assertEqual([[0, 'desc'],[1, 'asc']], default_sort_order)

    def submit_data(self, post_data):
        WebPlayer(self.manager).accept(Request(message=post_data, transportInfo=self.transport))

    def test_should_get_old_answer_for_submissions_which_is_submitted_before_MC_changed_to_other(self):
        """
        Function to test get old answer for submissions which is submitted before answer type changed from multiple choice/single choice to other type(word, number, date, GPS)
        """
        ddtype = create_default_ddtype(self.manager)
        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associatéd entity?",entity_question_flag=True, ddtype=ddtype)
        rp_field = DateField(label="Report date", code="RD", name="What is réporting date?",date_format="dd.mm.yyyy", event_time_field_flag=True, ddtype=ddtype)
        symptoms_field = SelectField(label="Zhat are symptoms?", code="SY", name="Zhat are symptoms?",
            options=[("Rapid weight loss", "a"), ("Dry cough", "b"), ("Pneumonia", "c"),
                     ("Memory loss", "d"), ("Neurological disorders ", "e")], single_select_flag=False, ddtype=ddtype)
        blood_type_field = SelectField(label="What is your blood group?", code="BG", name="What is your blood group?",
            options=[("O+", "a"), ("O-", "b"), ("AB", "c"), ("B+", "d")], single_select_flag=True, ddtype=ddtype)

        form_model = FormModelBuilder(self.manager, ['clinic'], form_code='cli001').add_fields(eid_field, rp_field,symptoms_field, blood_type_field).build()
        EntityBuilder(self.manager, ['clinic'], 'cid001').add_data([(MOBILE_NUMBER_FIELD, "919970059125", ddtype), (NAME_FIELD, "Ritesh", ddtype)]).build()

        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.12.2012', 'SY': 'ab', 'BG': 'b'})
        self._edit_fields(form_model, IntegerField(label="Zhat are symptoms?", code="SY", name="Zhat are symptoms?", ddtype=ddtype))

        submissions = successful_submissions(self.manager, form_model.form_code)
        analyzer = SubmissionAnalyzer(form_model, self.manager, Mock(), submissions)
        values = analyzer.get_raw_values()

        self.assertEqual([['Rapid weight loss','Dry cough'], ['O-']], values[0][4:])

    def test_should_get_old_answer_for_submissions_which_is_submitted_before_other_changed_to_MC(self):
        """
        Function to test get old answer for submissions which is submitted before answer type changed from other type(word, number, date, GPS) to multiple choice/single choice
        """
        ddtype = create_default_ddtype(self.manager)
        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associatéd entity?",entity_question_flag=True, ddtype=ddtype)
        rp_field = DateField(label="Report date", code="RD", name="What is réporting date?",date_format="dd.mm.yyyy", event_time_field_flag=True, ddtype=ddtype)
        symptoms_field = TextField(label="Zhat are symptoms?", code="SY", name="Zhat are symptoms?", ddtype=ddtype)
        blood_type_field = SelectField(label="What is your blood group?", code="BG", name="What is your blood group?",
            options=[("O+", "a"), ("O-", "b"), ("AB", "c"), ("B+", "d")], single_select_flag=True, ddtype=ddtype)

        form_model = FormModelBuilder(self.manager, ['clinic'], form_code='cli001').add_fields(eid_field, rp_field,symptoms_field, blood_type_field).build()
        EntityBuilder(self.manager, ['clinic'], 'cid001').add_data([(MOBILE_NUMBER_FIELD, "919970059125", ddtype), (NAME_FIELD, "Ritesh", ddtype)]).build()
        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.12.2012', 'SY': 'Fever', 'BG': 'b'})

        symptoms_field = SelectField(label="Zhat are symptoms?", code="SY", name="Zhat are symptoms?",
            options=[("Rapid weight loss", "a"), ("Dry cough", "b"), ("Pneumonia", "c"),
                     ("Memory loss", "d"), ("Neurological disorders ", "e")], single_select_flag=False, ddtype=ddtype)
        self._edit_fields(form_model, symptoms_field)
        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.12.2012', 'SY': 'ab', 'BG': 'b'})

        submissions = successful_submissions(self.manager, form_model.form_code)
        analyzer = SubmissionAnalyzer(form_model, self.manager, Mock(), submissions)
        values = analyzer.get_raw_values()

        self.assertEqual([['Rapid weight loss','Dry cough'], ['O-']], values[0][4:])
        self.assertEqual(['Fever', ['O-']], values[1][4:])

    def test_should_get_old_answer_for_submissions_which_is_submitted_before_other_changed_to_other(self):
        """
        Function to test get old answer for submissions which is submitted before answer type changed from other type(word, number, date, GPS) to other type
        """
        ddtype = create_default_ddtype(self.manager)
        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associatéd entity?",
            entity_question_flag=True, ddtype=ddtype)
        rp_field = DateField(label="Report date", code="RD", name="What is réporting date?", date_format="dd.mm.yyyy",
            event_time_field_flag=True, ddtype=ddtype)
        symptoms_field = TextField(label="Zhat are symptoms?", code="SY", name="Zhat are symptoms?", ddtype=ddtype)
        gps = TextField(label="What is your blood group?", code="GPS", name="What is your gps?", ddtype=ddtype)
        national_day_field = TextField(label="national day?", code="ND", name="national day", ddtype=ddtype)
        form_model = FormModelBuilder(self.manager, ['clinic'], form_code='cli001').add_fields(eid_field, rp_field,
            symptoms_field, gps, national_day_field).build()
        EntityBuilder(self.manager, ['clinic'], 'cid001').add_data([(MOBILE_NUMBER_FIELD, "919970059125", ddtype), (NAME_FIELD, "Ritesh", ddtype)]).build()

        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.12.2012', 'SY': 'Fever', 'GPS': 'NewYork', "ND":"oct 1"})

        gps = GeoCodeField(label="What is your blood group?", code="GPS", name="What is your gps?", ddtype=ddtype)
        symptoms_field = IntegerField(label="Zhat are symptoms?", code="SY", name="Zhat are symptoms?", ddtype=ddtype)
        national_day_field = DateField(label="national day?", code="ND", name="national day", ddtype=ddtype, date_format="dd.mm.yyyy")

        self._edit_fields(form_model, gps, national_day_field, symptoms_field)
        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.12.2012', 'SY': '100', 'GPS': '1,1', "ND":"01.10.2012"})

        submissions = successful_submissions(self.manager, form_model.form_code)
        analyzer = SubmissionAnalyzer(form_model, self.manager, Mock(), submissions)
        values = analyzer.get_raw_values()

        self.assertEqual(['100', '1,1', '01.10.2012'], values[0][4:])
        self.assertEqual(['Fever', 'NewYork', 'oct 1'], values[1][4:])

    def test_should_show_previous_submissions_in_old_format_after_change_date_format(self):
        ddtype = create_default_ddtype(self.manager)
        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associatéd entity?",
            entity_question_flag=True, ddtype=ddtype)
        rp_field = DateField(label="Report date", code="RD", name="What is réporting date?", date_format="dd.mm.yyyy",
            event_time_field_flag=True, ddtype=ddtype)

        form_model = FormModelBuilder(self.manager, ['clinic'], form_code='cli001').add_fields(eid_field, rp_field).build()
        EntityBuilder(self.manager, ['clinic'], 'cid001').add_data([(MOBILE_NUMBER_FIELD, "919970059125", ddtype), (NAME_FIELD, "Ritesh", ddtype)]).build()

        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.12.2012'})

        rp_field = DateField(label="Report date", code="RD", name="What is réporting date?", date_format="mm.yyyy",event_time_field_flag=True, ddtype=ddtype)
        self._edit_fields(form_model, rp_field)
        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'RD': '08.2012'})

        rp_field = DateField(label="Report date", code="RD", name="What is réporting date?", date_format="mm.dd.yyyy",event_time_field_flag=True, ddtype=ddtype)
        self._edit_fields(form_model, rp_field)
        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.24.2012'})

        submissions = successful_submissions(self.manager, form_model.form_code)
        analyzer = SubmissionAnalyzer(form_model, self.manager, Mock(), submissions)
        values = analyzer.get_raw_values()
        reporting_periods = map(lambda value: value[1], values)

        self.assertIn('08.2012', reporting_periods)
        self.assertIn('12.12.2012', reporting_periods)
        self.assertIn('12.24.2012', reporting_periods)

    def test_should_should_get_fields_values_after_question_count_changed(self):
        ddtype = create_default_ddtype(self.manager)
        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associatéd entity?",
            entity_question_flag=True, ddtype=ddtype)
        rp_field = DateField(label="Report date", code="RD", name="What is réporting date?", date_format="dd.mm.yyyy",
            event_time_field_flag=True, ddtype=ddtype)
        symptoms_field = TextField(label="Zhat are symptoms?", code="SY", name="Zhat are symptoms?", ddtype=ddtype)
        gps = TextField(label="What is your blood group?", code="GPS", name="What is your gps?", ddtype=ddtype)
        form_model = FormModelBuilder(self.manager, ['clinic'], form_code='cli001').add_fields(eid_field, rp_field,
            symptoms_field, gps).build()
        EntityBuilder(self.manager, ['clinic'], 'cid001').add_data([(MOBILE_NUMBER_FIELD, "919970059125", ddtype), (NAME_FIELD, "Ritesh", ddtype)]).build()

        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.12.2012', 'SY': 'Fever', 'GPS': 'NewYork'})

        form_model.create_snapshot()
        form_model.delete_field("SY")
        form_model.save()

        self.submit_data({'form_code': 'cli001', 'EID': 'cid001', 'RD': '12.12.2012', 'GPS': '1,1'})

        submissions = successful_submissions(self.manager, form_model.form_code)
        analyzer = SubmissionAnalyzer(form_model, self.manager, Mock(), submissions)
        values = analyzer.get_raw_values()

        self.assertEqual(['1,1'], values[0][4:])
        self.assertEqual(['NewYork'], values[1][4:])

    def _prepare_clinic_entity(self):
        entity = Entity(self.mocked_dbm, entity_type="Clinic", location=["India", "MH", "Pune"], short_code="cli14",
            geometry={'type': 'Point', 'coordinates': [1, 2]})
        entity._doc.data = {'name': {'value': 'Clinic-One'}}
        return entity

    def _prepare_analyzer_with_one_submission(self, form_model, values, with_status=False):
        with patch("project.submission_analyzer.SubmissionAnalyzer._init_raw_values"):
            submission = Submission(self.manager,
                transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                form_code=form_model.form_code,
                values=values)

            return SubmissionAnalyzer(form_model, self.manager, self.user, [submission], with_status=with_status)

    def _prepare_analyzer(self, form_model, values_list, keywords=None):
        with patch("project.submission_analyzer.SubmissionAnalyzer._init_raw_values"):
            submissions = []
            for values in values_list:
                submission = Submission(self.manager,
                    transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                    form_code=form_model.form_code,
                    values=values)
                submissions.append(submission)

            return SubmissionAnalyzer(form_model, self.manager, self.user, submissions, keywords)

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
