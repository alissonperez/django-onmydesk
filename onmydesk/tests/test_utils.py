from datetime import date, timedelta
from django.test import TestCase

from onmydesk.utils import str_to_date


class StrToDateTestCase(TestCase):

    def test_call_with_d_must_return_same_date(self):
        reference_date = date(2015, 4, 1)

        self.assertEqual(str_to_date('D', reference_date), reference_date)

    def test_call_with_subtraction_must_return_correct_date(self):
        reference_date = date(2015, 4, 1)

        self.assertEqual(str_to_date('D-1', reference_date),
                         reference_date - timedelta(days=1))

    def test_call_addition_must_return_correct_date(self):
        reference_date = date(2015, 4, 1)

        self.assertEqual(str_to_date('D+1', reference_date),
                         reference_date + timedelta(days=1))

    def test_value_with_space(self):
        reference_date = date(2015, 4, 1)

        self.assertEqual(str_to_date(' D - 1 ', reference_date),
                         reference_date - timedelta(days=1))

    def test_value_lowercase(self):
        reference_date = date(2015, 4, 1)

        self.assertEqual(str_to_date('d-1', reference_date),
                         reference_date - timedelta(days=1))

        self.assertEqual(str_to_date('d', reference_date),
                         reference_date)

    def test_wrong_value_must_raise_value_error(self):
        self.assertRaises(ValueError, str_to_date, 'A-1', date.today())
        self.assertRaises(ValueError, str_to_date, 'A1', date.today())
        self.assertRaises(ValueError, str_to_date, 'D-A', date.today())
        self.assertRaises(ValueError, str_to_date, 'A', date.today())
        self.assertRaises(ValueError, str_to_date, 'D++1', date.today())
        self.assertRaises(ValueError, str_to_date, '1-D', date.today())
