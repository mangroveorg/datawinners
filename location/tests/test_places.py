import json
import unittest
from django.test.client import Client

class TestPlaces(unittest.TestCase):
    def test_places(self):
        client = Client()
        response = client.get('/places', {'term': "soas"})
        grouped_places = json.loads(response.content)

        self.assertEqual('Commune',grouped_places[0]['category'])
        self.assertEqual('SOASERANA,MANJA,MENABE',grouped_places[0]['label'])

        self.assertEqual('Commune',grouped_places[1]['category'])
        self.assertEqual('SOASERANA,BETIOKY ATSIMO,ATSIMO ANDREFANA',grouped_places[1]['label'])
