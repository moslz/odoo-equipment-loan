import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EquipmentItem(models.Model):
    _name = 'equipment.item'
    _description = 'Equipment Item'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    name_key = fields.Char(
        compute='_compute_name_key',
        store=True,
        index=True,
    )
    active = fields.Boolean(default=True)
    notes = fields.Text(string='Notes')
    loan_ids = fields.One2many(
        'equipment.loan',
        'equipment_id',
        string='Loans',
    )

    @api.depends('name')
    def _compute_name_key(self):
        for item in self:
            item.name_key = re.sub(r'[\W_]+', '', (item.name or '').lower())

    @api.constrains('name')
    def _check_unique_name(self):
        for item in self:
            duplicates = self.with_context(active_test=False).search_count([
                ('id', '!=', item.id),
                ('name_key', '=', item.name_key),
            ])
            if duplicates:
                raise ValidationError(
                    _('An equipment item similar to "%s" already exists.', item.name)
                )
