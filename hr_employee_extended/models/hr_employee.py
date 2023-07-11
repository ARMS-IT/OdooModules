from odoo import api, fields, models, _


class HREmployee(models.Model):
    _inherit = 'hr.employee'
    _order = 'code' 
    
    code = fields.Char(string="Employee Code")

    @api.model
    def create(self, vals):
        res = super(HREmployee, self).create(vals)
        res['code'] = self.env['ir.sequence'].next_by_code('employee.code.sequence')
        return res
