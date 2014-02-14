from unittest import TestCase
from datawinners.project.views.datasenders import parse_successful_imports


class TestParseSuccessfulImports(TestCase):
    def test_should_parse_datasenders_with_all_fields(self):
        imported_datasenders = {
            "reporter_id":{"l": ["loc1", "loc2"], "s": "reporter_id", "n": "reporter_name", "g": [1.11, 2.22], "m": "12334534",
             "email": "reporter@email.com"},
            "reporter_id2":{"l": ["loc11", "loc22"], "s": "reporter_id2", "n": "reporter_name2", "g": [1.11, 2.22], "m": "123345341",
             "email": "reporter2@email.com"}
        }
        parsed_datasenders = parse_successful_imports(imported_datasenders)

        self.assertEqual(len(parsed_datasenders), 2)
        first_datasender = parsed_datasenders[0]
        self.assertEqual(first_datasender["name"], "reporter_name")
        self.assertEqual(first_datasender["location"], "loc1,loc2")
        self.assertEqual(first_datasender["id"], "reporter_id")
        self.assertEqual(first_datasender["email"], "reporter@email.com")
        self.assertEqual(first_datasender["mobile_number"], "12334534")
        self.assertEqual(first_datasender["coordinates"], "1.11,2.22")

        second_datasender = parsed_datasenders[1]
        self.assertEqual(second_datasender["name"], "reporter_name2")
        self.assertEqual(second_datasender["location"], "loc11,loc22")
        self.assertEqual(second_datasender["id"], "reporter_id2")
        self.assertEqual(second_datasender["email"], "reporter2@email.com")
        self.assertEqual(second_datasender["mobile_number"], "123345341")
        self.assertEqual(second_datasender["coordinates"], "1.11,2.22")

    def test_should_parse_datasenders_with_no_email_field(self):
        imported_datasenders = {"reporter_id":{"l": ["loc1", "loc2"], "s": "reporter_id", "n": "reporter_name", "g": [1.11, 2.22], "m": "12334534"}}

        parsed_datasenders = parse_successful_imports(imported_datasenders)

        self.assertEqual(len(parsed_datasenders), 1)
        first_datasender = parsed_datasenders[0]
        self.assertEqual(first_datasender["name"], "reporter_name")
        self.assertEqual(first_datasender["location"], "loc1,loc2")
        self.assertEqual(first_datasender["id"], "reporter_id")
        self.assertEqual(first_datasender["email"], "")
        self.assertEqual(first_datasender["mobile_number"], "12334534")
        self.assertEqual(first_datasender["coordinates"], "1.11,2.22")

    def test_should_parse_datasenders_with_no_coordinates_field(self):
        imported_datasenders = {"reporter_id":{"l": ["loc1", "loc2"], "s": "reporter_id", "n": "reporter_name", "m": "12334534",
             "email": "reporter@email.com"}}

        parsed_datasenders = parse_successful_imports(imported_datasenders)

        self.assertEqual(len(parsed_datasenders), 1)
        first_datasender = parsed_datasenders[0]
        self.assertEqual(first_datasender["name"], "reporter_name")
        self.assertEqual(first_datasender["location"], "loc1,loc2")
        self.assertEqual(first_datasender["id"], "reporter_id")
        self.assertEqual(first_datasender["email"], "reporter@email.com")
        self.assertEqual(first_datasender["mobile_number"], "12334534")
        self.assertEqual(first_datasender["coordinates"], "")

    def test_should_parse_datasenders_with_no_location_field(self):
        imported_datasenders = {"reporter_id":
            {"s": "reporter_id", "n": "reporter_name", "g": [1.11, 2.22], "m": "12334534",
             "email": "reporter@email.com"}
        }
        parsed_datasenders = parse_successful_imports(imported_datasenders)

        self.assertEqual(len(parsed_datasenders), 1)
        first_datasender = parsed_datasenders[0]
        self.assertEqual(first_datasender["name"], "reporter_name")
        self.assertEqual(first_datasender["location"], "")
        self.assertEqual(first_datasender["id"], "reporter_id")
        self.assertEqual(first_datasender["email"], "reporter@email.com")
        self.assertEqual(first_datasender["mobile_number"], "12334534")
        self.assertEqual(first_datasender["coordinates"], "1.11,2.22")
