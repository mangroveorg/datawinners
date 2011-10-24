from unittest.case import TestCase
import django

class TestBackport(TestCase):
    def test_assertFieldOutput_should_only_be_needed_until_it_included_in_django(self):
        self.assertEqual(django.VERSION, (1, 3, 0, 'final', 0), 'Backport should be reviewed due to the version upgrade of Django')
