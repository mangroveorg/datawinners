from unittest.case import TestCase
import django
from django.core.exceptions import ValidationError
from django.core.validators import EMPTY_VALUES
from django.forms.fields import CharField


# Method copied from DJango development version
# http://code.djangoproject.com/svn/!svn/bc/17029/django/trunk/django/test/testcases.py (Line 288)
def assertFieldOutput(test_case, fieldclass, valid, invalid, field_args=None,
                      field_kwargs=None, empty_value=u''):
    """
    Asserts that a form field behaves correctly with various inputs.

    Args:
        fieldclass: the class of the field to be tested.
        valid: a dictionary mapping valid inputs to their expected
                cleaned values.
        invalid: a dictionary mapping invalid inputs to one or more
                raised error messages.
        field_args: the args passed to instantiate the field
        field_kwargs: the kwargs passed to instantiate the field
        empty_value: the expected clean output for inputs in EMPTY_VALUES

    """
    if field_args is None:
        field_args = []
    if field_kwargs is None:
        field_kwargs = {}
    required = fieldclass(*field_args, **field_kwargs)
    optional = fieldclass(*field_args,
                          **dict(field_kwargs, required=False))
    # test valid inputs
    for input, output in valid.items():
        test_case.assertEqual(required.clean(input), output)
        test_case.assertEqual(optional.clean(input), output)
        # test invalid inputs
    for input, errors in invalid.items():
        with test_case.assertRaises(ValidationError) as context_manager:
            required.clean(input)
        test_case.assertEqual(context_manager.exception.messages, errors)

        with test_case.assertRaises(ValidationError) as context_manager:
            optional.clean(input)
        test_case.assertEqual(context_manager.exception.messages, errors)
        # test required inputs
    error_required = [u'This field is required.']
    for e in EMPTY_VALUES:
        with test_case.assertRaises(ValidationError) as context_manager:
            required.clean(e)
        test_case.assertEqual(context_manager.exception.messages,
                         error_required)
        test_case.assertEqual(optional.clean(e), empty_value)
        # test that max_length and min_length are always accepted
    if issubclass(fieldclass, CharField):
        field_kwargs.update({'min_length': 2, 'max_length': 20})
        test_case.assertTrue(isinstance(fieldclass(*field_args, **field_kwargs),
                                   fieldclass))
