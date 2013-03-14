import unittest
from django.forms import IntegerField, CharField, ChoiceField
from project.submission_form import SubmissionForm

class TestSubmissionForm(unittest.TestCase):

    def test_should_set_initial_values_for_submissions_with_lower_case_question_codes(self):

        initial_dict = {'q1': 'Ans1', 'q2': 'Ans2'}
        submission_form = SubmissionForm()
        submission_form.fields = {'q1': IntegerField(), 'q2': CharField()}

        submission_form.initial_values(initial_dict)

        self.assertEquals('Ans1', submission_form.fields.get('q1').initial)
        self.assertEquals('Ans2', submission_form.fields.get('q2').initial)


    def test_should_set_initial_values_for_submissions_with_upper_case_question_codes(self):

        initial_dict = {'Q1': 'Ans1', 'Q2': 'Ans2'}
        submission_form = SubmissionForm()
        submission_form.fields = {'Q1': IntegerField(), 'Q2': CharField()}

        submission_form.initial_values(initial_dict)

        self.assertEquals('Ans1', submission_form.fields.get('Q1').initial)
        self.assertEquals('Ans2', submission_form.fields.get('Q2').initial)
