import json
import unittest

from django.test import Client

from nose.plugins.attrib import attr
from framework.utils.common_utils import random_number
from tests.datasendertests.data_sender_activation_email_helper import create_questionnaire


class DataSenderActivationEmailTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = Client()
        cls.client.login(username='tester150411@gmail.com', password='tester150411')
        cls.project_id = create_questionnaire(cls.client)

    def _get_data_sender_data(self, with_email=False, with_project_id=False):
        short_code = "rep" + random_number(3)
        email = "email" + random_number(3) + "@mailinator.com"
        return {"geo_code": "",
                "name": "",
                "telephone_number": random_number(6).__str__(),
                "location": "",
                "project_id": self.project_id if with_project_id else "",
                "short_code": short_code,
                "email": email if with_email else ""}

    @attr("functional_test")
    def test_should_not_make_entry_in_postgres_when_contact_registered(self):
        data_sender_data = self._get_data_sender_data(with_email=True)
        short_code = data_sender_data['short_code']
        email = data_sender_data['email']

        response = self.client.post(
            path='/entity/datasender/register/',
            data=data_sender_data)
        self.assertTrue('Your contact(s) have been added. ID is: ' + short_code in response.content)

        response = self.client.post(path='/admin-apis/datasender/check_if_entry_made_in_postgres/',
                                    data={'ds_email': email})
        self.assertEqual(response.content, '{"found": false}')

    @attr("functional_test")
    def test_should_not_make_entry_in_postgres_when_contact_is_given_web_access(self):
        email = "email" + random_number(3) + "@mailinator.com"
        data_sender_data = self._get_data_sender_data()
        short_code = data_sender_data['short_code']
        response = self.client.post(
            path='/entity/datasender/register/',
            data=data_sender_data)
        self.assertTrue('Your contact(s) have been added. ID is: ' + short_code in response.content)
        web_access_data = {'post_data': ['[{"email":"' + email + '","reporter_id":"' + short_code + '"}]']}
        response = self.client.post(path='/entity/webuser/create',
                                    data=web_access_data)
        response_dict = json.loads(response.content)
        self.assertEquals(response_dict['message'], 'Users has been created')
        self.assertTrue(response_dict['success'])

        response = self.client.post(path='/admin-apis/datasender/check_if_entry_made_in_postgres/',
                                    data={'ds_email': email})
        self.assertEqual(response.content, '{"found": false}')

    @attr("functional_test")
    def test_should_make_entry_in_postgres_when_ds_registered(self):
        data_sender_data = self._get_data_sender_data(with_email=True, with_project_id=True)
        short_code = data_sender_data['short_code']
        email = data_sender_data['email']
        response = self.client.post(
            path='/entity/datasender/register/',
            data=data_sender_data)
        self.assertTrue('Registration successful. ID is: ' + short_code in response.content)

        response = self.client.post(path='/admin-apis/datasender/check_if_entry_made_in_postgres/',
                                    data={'ds_email': email})
        self.assertEqual(response.content, '{"found": true}')

    @attr("functional_test")
    def test_should_make_entry_in_postgres_when_contact_with_email_associated_to_questionnaire(self):
        data_sender_data = self._get_data_sender_data(with_email=True)
        short_code = data_sender_data['short_code']
        email = data_sender_data['email']

        response = self.client.post(
            path='/entity/datasender/register/',
            data=data_sender_data)
        self.assertTrue('Your contact(s) have been added. ID is: ' + short_code in response.content)

        associate_data = {'project_id': [self.project_id],
                          'ids': [short_code]}

        response = self.client.post(path='/entity/associate/',
                                    data=associate_data)
        response_dict = json.loads(response.content)
        self.assertEqual(response_dict['message'],
                         'Your Contact(s) have been added successfully. Contacts with an Email address added to a Questionnaire for the first time will receive an activation email with instructions.')
        self.assertTrue(response_dict['success'])

        response = self.client.post(path='/admin-apis/datasender/check_if_entry_made_in_postgres/',
                                    data={'ds_email': email})
        self.assertEqual(response.content, '{"found": true}')

    @attr("functional_test")
    def test_should_make_entry_in_postgres_when_ds_is_given_web_access(self):
        email = "email" + random_number(3) + "@mailinator.com"
        data_sender_data = self._get_data_sender_data()
        short_code = data_sender_data['short_code']
        response = self.client.post(
            path='/entity/datasender/register/',
            data=data_sender_data)
        self.assertTrue('Your contact(s) have been added. ID is: ' + short_code in response.content)

        associate_data = {'project_id': [self.project_id],
                          'ids': [short_code]}

        response = self.client.post(path='/entity/associate/',
                                    data=associate_data)
        response_dict = json.loads(response.content)
        self.assertEqual(response_dict['message'],
                         'Your Contact(s) have been added successfully. Contacts with an Email address added to a Questionnaire for the first time will receive an activation email with instructions.')
        self.assertTrue(response_dict['success'])

        web_access_data = {'post_data': ['[{"email":"' + email + '","reporter_id":"' + short_code + '"}]']}
        response = self.client.post(path='/entity/webuser/create',
                                    data=web_access_data)
        response_dict = json.loads(response.content)
        self.assertEquals(response_dict['message'], 'Users has been created')
        self.assertTrue(response_dict['success'])

        response = self.client.post(path='/admin-apis/datasender/check_if_entry_made_in_postgres/',
                                    data={'ds_email': email})
        self.assertEqual(response.content, '{"found": true}')

    @attr("functional_test")
    def test_should_make_entry_in_postgres_when_ds_edited_with_email(self):
        data_sender_data = self._get_data_sender_data()
        short_code = data_sender_data['short_code']
        email = "email" + random_number(3) + "@mailinator.com"

        response = self.client.post(
            path='/entity/datasender/register/',
            data=data_sender_data)
        self.assertTrue('Your contact(s) have been added. ID is: ' + short_code in response.content)

        associate_data = {'project_id': [self.project_id],
                          'ids': [short_code]}

        response = self.client.post(path='/entity/associate/',
                                    data=associate_data)
        response_dict = json.loads(response.content)
        self.assertEqual(response_dict['message'],
                         'Your Contact(s) have been added successfully. Contacts with an Email address added to a Questionnaire for the first time will receive an activation email with instructions.')
        self.assertTrue(response_dict['success'])

        data_sender_data['email'] = email
        response = self.client.post(path='/entity/datasender/edit/' + short_code + "/",
                                    data=data_sender_data)

        self.assertTrue('Your changes have been saved.' in response.content)

        response = self.client.post(path='/admin-apis/datasender/check_if_entry_made_in_postgres/',
                                    data={'ds_email': email})
        self.assertEqual(response.content, '{"found": true}')

    @attr("functional_test")
    def test_should_make_entry_in_postgres_when_ds_edited_with_email(self):
        data_sender_data = self._get_data_sender_data(with_project_id=True)
        short_code = data_sender_data['short_code']
        email = "email" + random_number(3) + "@mailinator.com"
        response = self.client.post(
            path='/entity/datasender/register/',
            data=data_sender_data)
        self.assertTrue('Registration successful. ID is: ' + short_code in response.content)

        data_sender_data['email'] = email
        response = self.client.post(path='/entity/datasender/edit/' + short_code + "/",
                                    data=data_sender_data)

        self.assertTrue('Your changes have been saved.' in response.content)

        response = self.client.post(path='/admin-apis/datasender/check_if_entry_made_in_postgres/',
                                    data={'ds_email': email})
        self.assertEqual(response.content, '{"found": true}')
