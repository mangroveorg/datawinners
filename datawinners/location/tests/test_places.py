import json

from django.test import TestCase
from django.test.client import Client


class TestPlaces(TestCase):
    fixtures = ['test_location_level.json', 'test_data.json']

    def test_places(self):
        client = Client()
        client.login(username="tester150411@gmail.com", password="tester150411")
        response = client.get('/places', {'term': "amb"})
        grouped_places = json.loads(response.content)

        self.assertTrue({u'category': u'Commune', u'label': u'AMBOANJO,MANAKARA ATSIMO,VATOVAVY FITOVINANY'} in grouped_places)
        self.assertTrue({u'category': u'Commune', u'label': u'AMBATOMANJAKA,MIARINARIVO,ITASY'} in grouped_places)
