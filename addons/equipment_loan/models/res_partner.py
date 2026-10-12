from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    equipment_loan_ids = fields.One2many(
        'equipment.loan',
        'borrower_id',
        string='Equipment Loans',
    )
    equipment_loan_count = fields.Integer(
        string='Loan Count',
        compute='_compute_equipment_loan_count',
    )

    @api.depends('equipment_loan_ids')
    def _compute_equipment_loan_count(self):
        for partner in self:
            partner.equipment_loan_count = len(partner.equipment_loan_ids)