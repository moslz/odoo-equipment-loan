from odoo import fields, models


class EquipmentLoan(models.Model):
    _name = 'equipment.loan'
    _description = 'Equipment Loan'

    name = fields.Char(string='Equipment', required=True)