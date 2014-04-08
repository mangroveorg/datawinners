import unittest
from django_digest.test import Client
from nose.plugins.attrib import attr
from framework.utils.common_utils import random_string
from tests.testdatasetup.project import create_multiple_unique_id_project, blood_test_project_name


class TestXform(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = Client()
        cls.client.login(username="tester150411@gmail.com", password="tester150411")
        cls.unique_id = random_string()
        cls.project_id = create_multiple_unique_id_project(cls.client, cls.unique_id)
        cls.client.set_authorization('tester150411@gmail.com', 'tester150411', method="Digest")
        cls.register_people_one(cls.client)

    @attr('functional_test')
    def test_xforms_list(self):
        response = self.client.get('/xforms/formList')
        self.assertTrue(blood_test_project_name(self.unique_id).lower() in response.content)

    @attr('functional_test')
    def test_xform_for_project(self):
        response = self.client.get('/xforms/%s' % self.project_id)
        self.assertTrue("<h:title>%s</h:title>"%blood_test_project_name(self.unique_id).lower() in response.content)
        self.assertTrue("<value>%s</value>"%self.people_one_id in response.content, response.content)
        self.assertTrue("<value>cid001</value>" in response.content, response.content)




    @classmethod
    def register_people_one(cls, client):
        cls.people_one_id = random_string()
        client.post('/entity/subject/create/people/', data={"form_code": "peo",  "q1":"First", "q2":"Last", "q3":"bangalore","q4" : "73,12", "q5":"1231231231","q6":cls.people_one_id, "t":"people"})