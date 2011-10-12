import json
from django.test import TestCase
from django.test.client import Client

class TestPlaces(TestCase):
    fixtures = ['test_location_level.json']

    def test_places(self):
        client = Client()
        response = client.get('/places', {'term': "amb"})
        grouped_places = json.loads(response.content)

        self.assertTrue({u'category': u'Commune', u'label': u'AMBOANJO,MANAKARA ATSIMO,VATOVAVY FITOVINANY'} in grouped_places)
        self.assertTrue({u'category': u'Commune', u'label': u'AMBATOMANJAKA,MIARINARIVO,ITASY'} in grouped_places)
