import json
from django.test import TestCase
from django.test.client import Client

class TestPlaces(TestCase):
    fixtures = ['test_location_level.json']

    def test_places(self):
        client = Client()
        response = client.get('/places', {'term': "amb"})
        grouped_places = json.loads(response.content)

        self.assertEqual('Commune',grouped_places[0]['category'])
        self.assertEqual('AMBATOMANJAKA,MIARINARIVO,ITASY',grouped_places[0]['label'])

        self.assertEqual('Commune',grouped_places[1]['category'])
        self.assertEqual('AMBOANJO,MANAKARA ATSIMO,VATOVAVY FITOVINANY',grouped_places[1]['label'])
