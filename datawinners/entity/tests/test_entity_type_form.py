import unittest
from datawinners.entity.forms import EntityTypeForm

class TestEntityTypeForm(unittest.TestCase):
    def test_entity_form_validation(self):
        values = [" 1 ", "a", " b", "c "]
        for value in values:
            form = EntityTypeForm({'entity_type_regex': value})
            self.assertTrue(form.is_valid())
  