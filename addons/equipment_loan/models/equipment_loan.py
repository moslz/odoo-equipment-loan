from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class EquipmentLoan(models.Model):
    _name = 'equipment.loan'
    _description = 'Equipment Loan'
    _order = 'date_start desc, id desc'

    equipment_id = fields.Many2one(
        'equipment.item',
        string='Equipment',
        required=True,
        ondelete='restrict',
    )
    borrower_id = fields.Many2one(
        'res.partner',
        string='Borrower',
        required=True,
        ondelete='restrict',
    )
    date_start = fields.Date(
        string='Loan Date',
        required=True,
        default=fields.Date.context_today,
    )
    date_end = fields.Date(string='Due Date', required=True)
    return_date = fields.Date(string='Returned On', readonly=True, copy=False)
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('borrowed', 'Borrowed'),
            ('returned', 'Returned'),
        ],
        string='Status',
        default='draft',
        required=True,
        readonly=True,
        copy=False,
    )
    notes = fields.Text(string='Notes')

    @api.depends('equipment_id.name', 'borrower_id.name')
    def _compute_display_name(self):
        for loan in self:
            parts = [loan.equipment_id.name, loan.borrower_id.name]
            loan.display_name = ' - '.join(filter(None, parts))

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for loan in self:
            if loan.date_end < loan.date_start:
                raise ValidationError(
                    _('The due date cannot be before the loan date.')
                )

    @api.constrains('equipment_id', 'date_start', 'date_end', 'state')
    def _check_no_overlap(self):
        for loan in self.filtered(lambda rec: rec.state != 'returned'):
            overlapping = self.search_count([
                ('id', '!=', loan.id),
                ('equipment_id', '=', loan.equipment_id.id),
                ('state', '!=', 'returned'),
                ('date_start', '<=', loan.date_end),
                ('date_end', '>=', loan.date_start),
            ])
            if overlapping:
                raise ValidationError(
                    _(
                        '"%s" is already loaned in this period.',
                        loan.equipment_id.name,
                    )
                )

    def action_confirm(self):
        for loan in self:
            if loan.state != 'draft':
                raise UserError(_('Only draft loans can be confirmed.'))
        self.write({'state': 'borrowed'})

    def action_return(self):
        for loan in self:
            if loan.state != 'borrowed':
                raise UserError(_('Only borrowed loans can be returned.'))
        self.write({
            'state': 'returned',
            'return_date': fields.Date.context_today(self),
        })