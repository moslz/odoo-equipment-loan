from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EquipmentItem(models.Model):
    _name = 'equipment.item'
    _description = 'Equipment Item'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)
    notes = fields.Text(string='Notes')
    loan_ids = fields.One2many(
        'equipment.loan',
        'equipment_id',
        string='Loans',
    )

    @api.constrains('name')
    def _check_unique_name(self):
        for item in self:
            duplicates = self.with_context(active_test=False).search_count([
                ('id', '!=', item.id),
                ('name', '=ilike', item.name),
            ])
            if duplicates:
                raise ValidationError(
                    _('An equipment item named "%s" already exists.', item.name)
                )