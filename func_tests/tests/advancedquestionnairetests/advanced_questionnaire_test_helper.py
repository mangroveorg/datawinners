import os
import re

from django.test import Client

from framework.utils.common_utils import by_css
from tests.testsettings import UI_TEST_TIMEOUT


DIR = os.path.dirname(__file__)
test_data = os.path.join(DIR, 'testdata')

def navigate_and_verify_web_submission_page_is_loaded(driver, global_navigation_page,project_name):
    all_data_page = global_navigation_page.navigate_to_all_data_page()
    web_submission_page = all_data_page.navigate_to_web_submission_page(project_name)
    form_element = verify_advanced_web_submission_page_is_loaded(driver)
    return form_element.get_attribute('id'), web_submission_page

def verify_advanced_web_submission_page_is_loaded(driver):
    form_element = driver.wait_for_element(UI_TEST_TIMEOUT, by_css("form"), True)
    driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_css(".ajax-loader"))
    return form_element

def perform_submission(file_name,project_temp_name,form_code,credentials):
    submission_data = open(os.path.join(test_data, file_name), 'r').read()
    submission_data = re.sub("tmpdt7nQf", project_temp_name, submission_data)
    submission_data = re.sub("<form_code>053", "<form_code>" + form_code, submission_data)
    client = Client()
    client.login(username=credentials.get('user'), password=credentials.get('password'))
    return client.post(path='/xlsform/web_submission/', data={'form_data': submission_data, 'form_code': form_code})

