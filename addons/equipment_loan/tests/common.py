from odoo.tests.common import TransactionCase


class EquipmentLoanCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.Item = cls.env['equipment.item']
        cls.Loan = cls.env['equipment.loan']
        cls.partner = cls.env['res.partner'].create({'name': 'Test Borrower'})
        cls.laptop = cls.Item.create({'name': 'Test Laptop 1'})
        cls.projector = cls.Item.create({'name': 'Test Projector'})

    def _create_loan(self, start, end, item=None):
        return self.Loan.create({
            'equipment_id': (item or self.laptop).id,
            'borrower_id': self.partner.id,
            'date_start': start,
            'date_end': end,
        })

    def _borrowed_loan(self, start, end, item=None):
        loan = self._create_loan(start, end, item)
        loan.action_confirm()
        return loan