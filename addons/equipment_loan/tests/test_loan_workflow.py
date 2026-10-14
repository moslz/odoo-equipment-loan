from datetime import date, datetime, timedelta
from unittest.mock import patch

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .common import EquipmentLoanCase

RETURN_TIME = datetime(2030, 1, 5, 14, 5, 0)


@tagged('post_install', '-at_install')
class TestLoanWorkflow(EquipmentLoanCase):

    def setUp(self):
        super().setUp()
        self.today = fields.Date.context_today(self.Loan)

    def test_new_loan_defaults(self):
        loan = self.Loan.create({
            'equipment_id': self.laptop.id,
            'borrower_id': self.partner.id,
            'date_end': self.today + timedelta(days=7),
        })
        self.assertEqual(loan.state, 'draft')
        self.assertEqual(loan.date_start, self.today)
        self.assertFalse(loan.returned_at)

    def test_display_name_combines_item_and_borrower(self):
        loan = self._create_loan(date(2030, 1, 1), date(2030, 1, 10))
        self.assertEqual(loan.display_name, 'Test Laptop 1 - Test Borrower')

    def test_confirm_sets_borrowed(self):
        loan = self._borrowed_loan(date(2030, 1, 1), date(2030, 1, 10))
        self.assertEqual(loan.state, 'borrowed')

    def test_return_records_exact_date_and_time(self):
        loan = self._borrowed_loan(date(2030, 1, 1), date(2030, 1, 10))
        with patch.object(fields.Datetime, 'now', return_value=RETURN_TIME):
            loan.action_return()
        self.assertEqual(loan.state, 'returned')
        self.assertEqual(loan.returned_at, RETURN_TIME)

    def test_invalid_transitions_raise_user_error(self):
        loan = self._create_loan(date(2030, 1, 1), date(2030, 1, 10))
        with self.assertRaises(UserError):
            loan.action_return()
        loan.action_confirm()
        with self.assertRaises(UserError):
            loan.action_confirm()
        loan.action_return()
        with self.assertRaises(UserError):
            loan.action_return()
        with self.assertRaises(UserError):
            loan.action_confirm()

    def test_failed_return_does_not_set_return_time(self):
        loan = self._create_loan(date(2030, 1, 1), date(2030, 1, 10))
        with self.assertRaises(UserError):
            loan.action_return()
        self.assertFalse(loan.returned_at)

    def test_confirm_multiple_loans_at_once(self):
        loans = (
            self._create_loan(date(2030, 1, 1), date(2030, 1, 10))
            | self._create_loan(date(2030, 1, 1), date(2030, 1, 10), self.projector)
        )
        loans.action_confirm()
        self.assertEqual(set(loans.mapped('state')), {'borrowed'})

    def test_batch_return_is_all_or_nothing(self):
        borrowed = self._borrowed_loan(date(2030, 1, 1), date(2030, 1, 10))
        draft = self._create_loan(date(2030, 1, 1), date(2030, 1, 10), self.projector)
        with self.assertRaises(UserError):
            (borrowed | draft).action_return()
        self.assertEqual(borrowed.state, 'borrowed')
        self.assertFalse(borrowed.returned_at)

    def test_copy_starts_as_fresh_draft(self):
        loan = self._borrowed_loan(date(2030, 1, 1), date(2030, 1, 10))
        loan.action_return()
        duplicate = loan.copy()
        self.assertEqual(duplicate.state, 'draft')
        self.assertFalse(duplicate.returned_at)

    def test_borrowed_loan_past_due_is_overdue(self):
        loan = self._borrowed_loan(self.today - timedelta(days=10), self.today - timedelta(days=1))
        self.assertTrue(loan.is_overdue)

    def test_loan_due_today_is_not_overdue(self):
        loan = self._borrowed_loan(self.today - timedelta(days=3), self.today)
        self.assertFalse(loan.is_overdue)

    def test_draft_loan_past_due_is_not_overdue(self):
        loan = self._create_loan(self.today - timedelta(days=10), self.today - timedelta(days=1))
        self.assertFalse(loan.is_overdue)

    def test_returned_loan_is_not_overdue(self):
        loan = self._borrowed_loan(self.today - timedelta(days=10), self.today - timedelta(days=1))
        loan.action_return()
        self.assertFalse(loan.is_overdue)