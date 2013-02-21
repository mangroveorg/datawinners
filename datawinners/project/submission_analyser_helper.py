from project.helper import get_org_id_by_user
from project.submission_analyzer import SubmissionAnalyzer

def get_analysis_result(filtered_submissions, form_model, manager, request):
    return SubmissionAnalyzer(form_model, manager, get_org_id_by_user(request.user),
        filtered_submissions, request.POST.get('keyword', '')).analyse()
