from datetime import date

from odoo.exceptions import AccessError
from odoo.tests.common import new_test_user, tagged

from .common import EquipmentLoanCase


@tagged('post_install', '-at_install')
class TestAccessRights(EquipmentLoanCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.internal_user = new_test_user(
            cls.env, login='plain_internal', groups='base.group_user',
        )
        cls.loan_user = new_test_user(
            cls.env, login='loan_user',
            groups='equipment_loan.group_equipment_loan_user',
        )
        cls.loan_manager = new_test_user(
            cls.env, login='loan_manager',
            groups='equipment_loan.group_equipment_loan_manager',
        )

    def test_user_without_role_cannot_read_loans(self):
        with self.assertRaises(AccessError):
            self.Loan.with_user(self.internal_user).search([])

    def test_user_can_run_full_loan_workflow(self):
        loan = self.Loan.with_user(self.loan_user).create({
            'equipment_id': self.laptop.id,
            'borrower_id': self.partner.id,
            'date_start': date(2030, 1, 1),
            'date_end': date(2030, 1, 10),
        })
        loan.action_confirm()
        loan.action_return()
        self.assertEqual(loan.state, 'returned')
        self.assertTrue(loan.returned_at)

    def test_user_can_read_equipment(self):
        items = self.Item.with_user(self.loan_user).search([])
        self.assertIn(self.laptop, items)

    def test_user_cannot_create_equipment(self):
        with self.assertRaises(AccessError):
            self.Item.with_user(self.loan_user).create({'name': 'Tablet'})

    def test_user_cannot_edit_equipment(self):
        with self.assertRaises(AccessError):
            self.laptop.with_user(self.loan_user).write({'name': 'Renamed'})

    def test_user_cannot_delete_loan(self):
        loan = self._create_loan(date(2030, 1, 1), date(2030, 1, 10))
        with self.assertRaises(AccessError):
            loan.with_user(self.loan_user).unlink()

    def test_manager_can_create_equipment(self):
        item = self.Item.with_user(self.loan_manager).create({'name': 'Tablet'})
        self.assertTrue(item.exists())

    def test_manager_can_delete_loan(self):
        loan = self._create_loan(date(2030, 1, 1), date(2030, 1, 10))
        loan.with_user(self.loan_manager).unlink()
        self.assertFalse(loan.exists())