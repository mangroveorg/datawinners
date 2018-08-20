import json
import os
import re

from django.test import Client

from framework.utils.common_utils import by_css
from tests.testsettings import UI_TEST_TIMEOUT

DIR = os.path.dirname(__file__)
test_data = os.path.join(DIR, 'testdata')


def navigate_and_verify_web_submission_page_is_loaded(driver, global_navigation_page, project_name):
    all_data_page = global_navigation_page.navigate_to_all_data_page()
    web_submission_page = all_data_page.navigate_to_web_submission_page(project_name)
    form_element = verify_advanced_web_submission_page_is_loaded(driver)
    return form_element.get_attribute('id'), web_submission_page


def navigate_and_verify_advanced_web_submission_page_is_loaded(driver, global_navigation_page, project_name):
    all_data_page = global_navigation_page.navigate_to_all_data_page()
    web_submission_page = all_data_page.navigate_to_advanced_web_submission_page(project_name)
    form_element = verify_advanced_web_submission_page_is_loaded(driver)
    return form_element.get_attribute('id'), web_submission_page


def verify_advanced_web_submission_page_is_loaded(driver):
    form_element = driver.wait_for_element(UI_TEST_TIMEOUT, by_css("form"), True)
    driver.wait_until_element_is_not_present(UI_TEST_TIMEOUT, by_css(".ajax-loader"))
    return form_element


def perform_submission(file_name, project_temp_name, form_code, credentials, image_upload=False):
    submission_data = open(os.path.join(test_data, file_name), 'r').read()
    submission_data = re.sub("tmpdt7nQf", project_temp_name, submission_data)
    submission_data = re.sub("<form_code>062", "<form_code>" + form_code, submission_data)
    return do_web_submission(form_code, submission_data, credentials, image_upload)


def do_web_submission(form_code, submission_data, credentials, image_upload=False):
    client = Client()
    client.login(username=credentials.get('username'), password=credentials.get('password'))
    data = {'form_data': submission_data, 'form_code': form_code}
    if image_upload:
        data = {'form_data': submission_data, 'form_code': form_code,
                'locate.png': open(DIR + '/testdata/' + 'locate.png', 'rb')}
    return client.post(path='/xlsform/web_submission/', data=data)


def delete_submissions(project_id, id_list, credentials):
    client = Client()
    client.login(username=credentials.get('username'), password=credentials.get('password'))
    data = {'id_list': json.dumps(id_list)}
    return client.post(path='/project/' + project_id + '/submissions/delete/', data=data)


def create_advance_questionnaire(project_name, test_data_path, file_name, credentials):
    client = Client()
    client.login(username=credentials.get('username'), password=credentials.get('password'))
    response = client.post(
        path='/xlsform/upload/?pname=' + project_name + '&qqfile='+file_name,
        data=open(os.path.join(test_data_path, file_name), 'r').read(),
        content_type='application/octet-stream')
    return response


def delete_advance_questionnaire(project_id, credentials):
    client = Client()
    client.login(username=credentials.get('username'), password=credentials.get('password'))
    return client.get(path='/project/delete/' + project_id + '/')
