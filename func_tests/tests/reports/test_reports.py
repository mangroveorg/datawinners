# vim: ai ts=4 sts=4 et sw= encoding=utf-8
import copy
import json
import csv
import os

import time
from mock import Mock
import re

import sys
import traceback

from django.contrib.auth.models import User
from django.test import Client
from mangrove.datastore.report_config import ReportConfig
from mangrove.form_model.project import Project
from nose.plugins.attrib import attr

from datawinners.main.database import get_database_manager
from datawinners.report.admin import create_report_view, delete_report_view
from datawinners.utils import random_string
from framework.base_test import HeadlessRunnerTest, setup_driver
from pages.loginpage.login_page import login
from tests.advancedquestionnairetests.advanced_questionnaire_test_helper import create_advance_questionnaire, \
    delete_advance_questionnaire, perform_submission, do_web_submission, delete_submissions
from tests.logintests.login_data import VALID_CREDENTIALS

DIR = os.path.dirname(__file__)


class TestReports(HeadlessRunnerTest):

    @classmethod
    def setUpClass(cls):
        cls.test_passed = True
        cls.driver = setup_driver("phantom")
        cls.admin_email_id = 'tester150411@gmail.com'
        cls.global_navigation_page = login(cls.driver, VALID_CREDENTIALS)
        cls.client = Client()
        cls.client.login(username=cls.admin_email_id, password='tester150411')
        cls.testdata = os.path.join(DIR, 'testdata')
        cls.user = User.objects.get(username=VALID_CREDENTIALS.get('username'))

    @attr('functional_test')
    def test_should_show_reports(self):
        self.project_name = random_string()
        self.report_name = random_string()
        file_name = 'test_questionnaire.xlsx'
        template_file_name = os.path.join(self.testdata, 'index.html')
        response = create_advance_questionnaire(self.project_name, self.testdata, file_name, VALID_CREDENTIALS)
        self.assertEquals(response.status_code, 200)
        self.assertNotEqual(response._container[0].find('project_name'), -1)
        response = json.loads(response._container[0])
        self.project_id = response.get('project_id')
        self.form_code = response['form_code']
        self.submission_ids = self._do_web_submissions()
        self.report = self._create_report_config(self.report_name, self.project_id, template_file_name)
        self._create_views(self.report)
        report_page = self.global_navigation_page.navigate_to_reports_page()
        report_page.navigate_to_report(self.report_name)
        time.sleep(60)  # This waiting is for ajax calls on report page
        self.assertEquals(len(self.submission_ids), report_page.get_number_of_records())
        delete_submissions(self.project_id, self.submission_ids[:1], VALID_CREDENTIALS)
        report_page.navigate_to_report(self.report_name)
        time.sleep(60)  # This waiting is for ajax calls on report page
        self.assertEquals(len(self.submission_ids) - 1, report_page.get_number_of_records())

    def _do_web_submissions(self):
        submission_ids = []
        submission_template = open(os.path.join(self.testdata, 'submission_data.xml'), 'r').read()
        submission_template = re.sub("\{\{tmp_id}}", "tmpIdas3e234", submission_template)
        submission_template = re.sub("\{\{form_code}}", self.form_code, submission_template)
        headers = []
        with open(os.path.join(self.testdata, 'submission_data.csv'), 'r') as csvfile:
            data_file = csv.reader(csvfile, delimiter=',')
            for line_number, line in enumerate(data_file):
                submission_data = copy.copy(submission_template)
                if line_number == 0:
                    headers = line
                else:
                    for index, field in enumerate(line):
                        submission_data = re.sub("\{\{" + headers[index] + "}}", field, submission_data)
                    response = do_web_submission(self.form_code, submission_data, VALID_CREDENTIALS)
                    submission_ids.append(response._headers['submission_id'][1])
                    self.assertEquals(response.status_code, 201)
        return submission_ids

    def _create_report_config(self, report_name, project_id, template=None):
        dbm = get_database_manager(User.objects.get(username=VALID_CREDENTIALS.get('username')))
        report = ReportConfig(dbm, report_name, [{"alias": "q1", "id": project_id}])
        report.save()
        dbm.put_attachment(report._doc, open(template, 'r'), 'index.html')
        return report

    def _create_views(self, report):
        request = Mock()
        request.user = self.user
        response = create_report_view(request, report.id)
        time.sleep(20)
        self.assertEquals(response.status_code, 200)

    def _delete_views(self, report):
        request = Mock()
        request.user = self.user
        response = delete_report_view(request, report.id)
        self.assertEquals(response.status_code, 200)

    def tearDown(self):
        print '--------------------'
        print 'Sweeping out all'
        print '--------------------'
        self._delete_views(self.report)
        self.report.delete()
        # delete questionnaire does a http redirection. so no assertion on its response
        delete_advance_questionnaire(self.project_id, VALID_CREDENTIALS)

