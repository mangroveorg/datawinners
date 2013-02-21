from datawinners.project.submission_data import SubmissionData
from project.Header import Header
from project.analysis_result import AnalysisResult
from project.data_sender import DataSender
from project.submission_utils.submission_formatter import SubmissionFormatter

class Analysis(SubmissionData):
    def __init__(self, form_model, manager, org_id, filters, keyword=None):
        super(Analysis, self).__init__(form_model, manager, org_id, Header, None, filters,keyword)
#        self._init_excel_values()

    def get_leading_part(self):
        leading_part = []
        for submission in self.filtered_submissions:
            data_sender, rp, subject, submission_date = super(Analysis, self)._get_submission_details(submission)
            leading_part.append(
                filter(lambda x: x, [submission.id, subject, rp, submission_date, data_sender]))
        return leading_part

    def _init_raw_values(self):
        leading_part = self.get_leading_part()
        self.populate_submission_data(leading_part)

    def analyse(self):
        field_values = SubmissionFormatter().get_formatted_values_for_list(self.get_raw_values())
        analysis_statistics = self.get_analysis_statistics()
        data_sender_list = self.get_data_senders()
        subject_lists = self.get_subjects()
        default_sort_order = self.get_default_sort_order()

        return AnalysisResult(field_values, analysis_statistics, data_sender_list, subject_lists, default_sort_order)

    def _get_leading_part_for_excel(self):
        leading_part = []
        for submission in self.filtered_submissions:
            data_sender_tuple, rp, subject_tuple, submission_date = super(Analysis, self)._get_submission_details(submission)
            subject_id  = subject_tuple[1]
            subject_name = subject_tuple[0]
            data_sender = DataSender.from_tuple(data_sender_tuple)
            leading_part.append(
                filter(lambda x: x, [submission.id, subject_name , subject_id, rp, submission_date, data_sender.name, data_sender.reporter_id]))
        return leading_part

    def _init_excel_values(self):
        leading_part_for_excel = self._get_leading_part_for_excel()
        self.populate_submission_data_for_excel(leading_part_for_excel)
