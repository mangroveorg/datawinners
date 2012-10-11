# encoding=utf-8
from datetime import datetime
import unittest
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import Entity
from mangrove.form_model.field import TextField, SelectField, DateField, field_attributes, GeoCodeField
from mangrove.form_model.form_model import FormModel
from mangrove.transport.facade import TransportInfo
from mangrove.transport.submissions import Submission
from mock import Mock, patch
from project.submission_analyzer import SubmissionAnalyzer, get_formatted_values_for_list, NULL

today = datetime.utcnow().strftime("%d.%m.%Y")

class SubmissionAnalyzerTest(unittest.TestCase):
    def setUp(self):
        self.manager = Mock(spec=DatabaseManager)
        self.request = Mock()

    def test_should_get_option_values_for_questions_case_insensitively(self):
        form_model = self._prepare_form_model(self.manager)
        data = {"eid": "cli14", "RD": "01.01.2012", "SY": "A2bC", "BG": "D"}
        analyzer = self._prepare_analyzer_with_one_submission(form_model, data)

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
        row = {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"}
        expected = {"eid": "cli14","RD": "01.01.2012", "SY": ['Rapid weight loss', 'Dry cough', 'Pneumonia'], "BG": ['B+']}
        form_model = self._prepare_form_model(self.manager)
        self._prepare_analyzer_with_one_submission(form_model, row)._replace_option_with_real_answer_value(row)
        self.assertEqual(expected, row)

    def test_should_get_leading_part_for_non_summary_project(self):
        form_model = self._prepare_form_model(self.manager)
        analyzer = self._prepare_analyzer_with_one_submission(form_model, {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"})

        with patch("project.submission_analyzer.get_data_sender") as get_data_sender, patch(
            "project.submission_analyzer.get_by_short_code") as get_by_short_code:
            get_data_sender.return_value = ('name', 'id', 'from')
            get_by_short_code.return_value = self._prepare_clinic_entity()
            leading_part = analyzer._get_leading_part()
            expected = [[('Clinic-One', 'cli14'), '01.01.2012', today, ('name', 'id', 'from')]]
            self.assertEqual(expected, leading_part)

    def test_should_get_leading_part_for_summary_project(self):
        form_model = self._prepare_summary_form_model(self.manager)
        analyzer = self._prepare_analyzer_with_one_submission(form_model, {"eid": "rep01", "SY": "a2bc", "BG": "d"})

        with patch("project.submission_analyzer.get_data_sender") as get_data_sender, patch(
            "project.submission_analyzer.get_by_short_code") as get_by_short_code:
            get_data_sender.return_value = ('name', 'id', 'from')
            get_by_short_code.return_value = self._prepare_clinic_entity()
            leading_part = analyzer._get_leading_part()
            expected = [[today, ('name', 'id', 'from')]]
            self.assertEqual(expected, leading_part)

    def test_should_get_raw_field_values(self):
        form_model = self._prepare_form_model(self.manager)
        analyzer = self._prepare_analyzer_with_one_submission(form_model, {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"})

        with patch("project.submission_analyzer.get_data_sender") as get_data_sender, patch(
            "project.submission_analyzer.get_by_short_code") as get_by_short_code:
            get_data_sender.return_value = ('name', 'id', 'from')
            get_by_short_code.return_value = self._prepare_clinic_entity()
            analyzer._init_raw_values()
            raw_field_values = analyzer.get_raw_values()
            expected = [[('Clinic-One', 'cli14'),  '01.01.2012', today, ('name', 'id', 'from'), ['Rapid weight loss', 'Dry cough', 'Pneumonia'], ['B+']]]
            self.assertEqual(expected, raw_field_values)

    def test_should_get_raw_field_values_filtered_by_keyword(self):

        form_model = self._prepare_form_model(self.manager)
        data = [{"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"},
              {"eid": "cli15", "RD": "02.02.2012", "SY": "c", "BG": "d"}]
        analyzer = self._prepare_analyzer(form_model, data, "Rapid")

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
        form_model = self._prepare_form_model(self.manager)
        analyzer = self._prepare_analyzer_with_one_submission(form_model, {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"})
        analyzer.filtered_leading_part =  [[('Clinic-2', 'cli14'),  '01.01.2012', today, ('name', 'id', 'from')],
                                              [('Clinic-1', 'cli15'),  '01.01.2011', today, ('name_2', 'id_2', 'from_2')],
                                              [('Clinic-1', 'cli15'),  '01.10.2011', today, ('name_3', 'id_3', 'from_3')]]
        subject_list = analyzer.get_subjects()
        expected = [('Clinic-1', 'cli15'), ('Clinic-2', 'cli14')]
        self.assertEqual(expected, subject_list)

    def test_should_get_data_sender_list(self):
        form_model = self._prepare_form_model(self.manager)
        analyzer = self._prepare_analyzer_with_one_submission(form_model, {"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"})

        analyzer.filtered_leading_part = [[('Clinic-2', 'cli14'),  '01.01.2012', today, ('name_2', 'id_2', 'from_2')],
                                          [('Clinic-1', 'cli15'),  '01.01.2011', today, ('name_1', 'id_1', 'from_1')],
                                          [('Clinic-3', 'cli16'),  '01.10.2011', today, ('name_2', 'id_2', 'from_2')]]

        data_sender_list = analyzer.get_data_senders()
        expected = [('name_1', 'id_1', 'from_1'), ('name_2', 'id_2', 'from_2')]
        self.assertEqual(expected, data_sender_list)

    def test_should_get_statistic_result(self):
        #question name ordered by field
        #options ordered by count(asc),option(alphabetic)
        #total = submission count of this question
        form_model = self._prepare_form_model(self.manager)
        d_ = [{"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"},
              {"eid": "cli14", "RD": "01.01.2012", "BG": "c"}
             ]
        analyzer = self._prepare_analyzer(form_model, d_)

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

    def test_should_format_field_values_to_list_presentation(self):
        raw_values = [[('Clinic-One', 'cli14'), '01.01.2012', today, ('name', 'id', 'from'), ['one', 'two', 'three'], ['B+']]]
        formatted_field_value = get_formatted_values_for_list(raw_values, '%s<span class="small_grey">%s</span>')
        expected = [['Clinic-One<span class="small_grey">cli14</span>',  '01.01.2012', today, 'name<span class="small_grey">id</span>', 'one, two, three', 'B+']]
        self.assertEqual(expected, formatted_field_value)

    def test_should_format_field_values_to_list_exported(self):
        raw_values = [[('Clinic-One', 'cli14'), '01.01.2012', today, ('name', 'id', 'from'), ['one', 'two', 'three'], ['B+']]]
        formatted_field_value = get_formatted_values_for_list(raw_values, '%s(%s)')
        expected = [['Clinic-One(cli14)',  '01.01.2012', today, 'name(id)', 'one, two, three', 'B+']]
        self.assertEqual(expected, formatted_field_value)

    def test_should_show_NULL_string_as_values_for_newly_created_questions(self):
        raw_values = [[('Clinic-One', 'cli14'), '01.01.2012', today, ('name', 'id', 'from'), ['one', 'two', 'three'], ['B+'], None, ""]]
        formatted_field_value = get_formatted_values_for_list(raw_values)
        expected = [['Clinic-One<span class="small_grey">cli14</span>',  '01.01.2012', today, 'name<span class="small_grey">id</span>', 'one, two, three', 'B+', NULL, NULL]]
        self.assertEqual(expected, formatted_field_value)


    def test_should_create_header_list_with_data_sender_if_the_project_is_not_a_summary_project(self):

        form_model = self._prepare_form_model(self.manager)
        d_ = [{"eid": "cli14", "RD": "01.01.2012", "SY": "a2bc", "BG": "d"},
                {"eid": "cli14", "RD": "01.01.2012", "BG": "c"}]
        analyzer = self._prepare_analyzer(form_model, d_)

        actual_header_list = analyzer.get_headers()

        expected_header = (["Clinic", "Reporting Period", "Submission Date", "Data Sender", "Zhat are symptoms?", "What is your blood group?"],
                           ["", 'dd.mm.yyyy', 'dd.mm.yyyy', "", "", ""])
        self.assertEqual(expected_header, actual_header_list)

    def test_should_create_header_list_without_reporter_column_if_the_project_is_a_summary_project(self):
        form_model = self._prepare_summary_form_model(self.manager)
        analyzer = self._prepare_analyzer_with_one_submission(form_model, {"eid": "rep01", "SY": "a2bc", "BG": "d"})

        actual_list = analyzer.get_headers()
        expected_header = (["Submission Date", "Data Sender", "Zhat are symptoms?", "What is your blood group?"],
                        ['dd.mm.yyyy', '', '', ''])
        self.assertEqual(expected_header, actual_list)


    def test_should_create_header_list_with_gps_type(self):
        form_model = self._prepare_form_model_with_gps_question(self.manager)
        analyzer = self._prepare_analyzer_with_one_submission(form_model, {"eid": "cli14", "gps": "2,3"})

        actual_list = analyzer.get_headers()
        expected_header = (["Clinic", "Submission Date", "Data Sender", "Where do you stay?"],
                           ['','dd.mm.yyyy', "", "gps"])
        self.assertEqual(expected_header, actual_list)

    def _prepare_form_model(self, manager):
        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associatéd entity?",
            language="en", entity_question_flag=True, ddtype=Mock())
        rp_field = DateField(label="Report date", code="RD", name="What is réporting date?",
            date_format="dd.mm.yyyy", event_time_field_flag=True, ddtype=Mock(),
            instruction="Answer must be a date in the following format: day.month.year. Example: 25.12.2011")
        symptoms_field = SelectField(label="Zhat are symptoms?", code="SY", name="Zhat are symptoms?",
            options=[("Rapid weight loss", "a"), ("Dry cough", "2b"), ("Pneumonia", "c"),
                     ("Memory loss", "d"), ("Neurological disorders ", "e")], single_select_flag=False, ddtype=Mock())
        blood_type_field = SelectField(label="What is your blood group?", code="BG", name="What is your blood group?",
            options=[("O+", "a"), ("O-", "b"), ("AB", "c"), ("B+", "d")], single_select_flag=True, ddtype=Mock())
        form_model = FormModel(manager, name="AIDS", label="Aids form_model", form_code="cli002", type='survey',
            fields=[eid_field, rp_field, symptoms_field, blood_type_field], entity_type=["clinic"])
        return form_model

    def _prepare_form_model_with_gps_question(self, manager):
        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associatéd entity?",
            language="en", entity_question_flag=True, ddtype=Mock())
        gps_field = GeoCodeField(name="field1_Loc", code="gps", label="Where do you stay?", ddtype=Mock(),
            language="en")
        form_model = FormModel(manager, name="AIDS", label="Aids form_model", form_code="cli002", type='survey',
            fields=[eid_field,gps_field], entity_type=["clinic"])
        return form_model

    def _prepare_summary_form_model(self, manager):
        eid_field = TextField(label="What is associated entity?", code="EID", name="What is associatéd entity?",
            language="en", entity_question_flag=True, ddtype=Mock())
        symptoms_field = SelectField(label="Zhat are symptoms?", code="SY", name="Zhat are symptoms?",
            options=[("Rapid weight loss", "a"), ("Dry cough", "2b"), ("Pneumonia", "c"),
                     ("Memory loss", "d"), ("Neurological disorders ", "e")], single_select_flag=False, ddtype=Mock())
        blood_type_field = SelectField(label="What is your blood group?", code="BG", name="What is your blood group?",
            options=[("O+", "a"), ("O-", "b"), ("AB", "c"), ("B+", "d")], single_select_flag=True, ddtype=Mock())
        form_model = FormModel(manager, name="AIDS", label="Aids form_model", form_code="cli002", type='survey',
            fields=[eid_field, symptoms_field, blood_type_field], entity_type=["reporter"])
        return form_model

    def _prepare_clinic_entity(self):
        entity = Entity(self.manager, entity_type="Clinic", location=["India", "MH", "Pune"], short_code="cli14",
            geometry={'type': 'Point', 'coordinates': [1, 2]})
        entity._doc.data = {'name': {'value': 'Clinic-One'}}
        return entity

    def _prepare_analyzer_with_one_submission(self, form_model, values, keywords=''):
        with patch("project.submission_analyzer.filter_submissions") as filter_submissions, patch(
            "project.submission_analyzer.SubmissionAnalyzer._init_raw_values") as _init_raw_values:
            submission = Submission(self.manager,
                transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                form_code=form_model.form_code,
                values=values)
            filter_submissions.return_value = [submission]
            return SubmissionAnalyzer(form_model, self.manager, self.request, None)

    def _prepare_analyzer(self, form_model, values_list, keywords=None):
        with patch("project.submission_analyzer.filter_submissions") as filter_submissions, patch(
            "project.submission_analyzer.SubmissionAnalyzer._init_raw_values") as _init_raw_values:
            return_value = []
            for values in values_list:
                submission = Submission(self.manager,
                    transport_info=TransportInfo('web', 'tester150411@gmail.com', 'destination'),
                    form_code=form_model.form_code,
                    values=values)
                return_value.append(submission)
            filter_submissions.return_value = return_value

            return SubmissionAnalyzer(form_model, self.manager, self.request, None, keywords)
