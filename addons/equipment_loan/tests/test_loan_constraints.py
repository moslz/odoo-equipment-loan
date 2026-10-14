from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests.common import tagged

from .common import EquipmentLoanCase


@tagged('post_install', '-at_install')
class TestLoanConstraints(EquipmentLoanCase):

    def test_due_date_before_loan_date_is_rejected(self):
        with self.assertRaises(ValidationError):
            self._create_loan(date(2030, 1, 10), date(2030, 1, 5))

    def test_same_day_loan_is_allowed(self):
        loan = self._create_loan(date(2030, 1, 10), date(2030, 1, 10))
        self.assertTrue(loan.exists())

    def test_overlapping_periods_are_rejected(self):
        self._borrowed_loan(date(2030, 1, 1), date(2030, 1, 10))
        cases = {
            'identical': (date(2030, 1, 1), date(2030, 1, 10)),
            'overlaps end': (date(2030, 1, 8), date(2030, 1, 15)),
            'overlaps start': (date(2029, 12, 28), date(2030, 1, 2)),
            'inside': (date(2030, 1, 3), date(2030, 1, 5)),
            'encloses': (date(2029, 12, 25), date(2030, 1, 20)),
            'starts on due date': (date(2030, 1, 10), date(2030, 1, 12)),
            'ends on loan date': (date(2029, 12, 30), date(2030, 1, 1)),
        }
        for label, (start, end) in cases.items():
            with self.subTest(case=label), self.assertRaises(ValidationError):
                self._create_loan(start, end)

    def test_adjacent_periods_are_allowed(self):
        self._borrowed_loan(date(2030, 1, 1), date(2030, 1, 10))
        before = self._create_loan(date(2029, 12, 20), date(2029, 12, 31))
        after = self._create_loan(date(2030, 1, 11), date(2030, 1, 15))
        self.assertTrue(before.exists() and after.exists())

    def test_other_equipment_is_not_blocked(self):
        self._borrowed_loan(date(2030, 1, 1), date(2030, 1, 10))
        loan = self._create_loan(date(2030, 1, 1), date(2030, 1, 10), self.projector)
        self.assertTrue(loan.exists())

    def test_draft_loan_also_reserves_equipment(self):
        self._create_loan(date(2030, 1, 1), date(2030, 1, 10))
        with self.assertRaises(ValidationError):
            self._create_loan(date(2030, 1, 5), date(2030, 1, 6))

    def test_returned_loan_frees_equipment(self):
        first = self._borrowed_loan(date(2030, 1, 1), date(2030, 1, 10))
        first.action_return()
        second = self._create_loan(date(2030, 1, 1), date(2030, 1, 10))
        self.assertEqual(second.state, 'draft')

    def test_editing_into_overlap_is_rejected(self):
        self._create_loan(date(2030, 1, 1), date(2030, 1, 10))
        later = self._create_loan(date(2030, 1, 11), date(2030, 1, 15))
        with self.assertRaises(ValidationError):
            later.write({'date_start': date(2030, 1, 9)})

    def test_editing_loan_does_not_conflict_with_itself(self):
        loan = self._create_loan(date(2030, 1, 1), date(2030, 1, 10))
        loan.write({'date_end': date(2030, 1, 20)})
        self.assertEqual(loan.date_end, date(2030, 1, 20))

    def test_editing_due_date_before_loan_date_is_rejected(self):
        loan = self._create_loan(date(2030, 1, 5), date(2030, 1, 10))
        with self.assertRaises(ValidationError):
            loan.write({'date_end': date(2030, 1, 1)})
