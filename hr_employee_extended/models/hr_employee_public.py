from odoo import api, fields, models, _


class HREmployeePublic(models.Model):
    _inherit = 'hr.employee.public'
    _order = 'code' 
    
    code = fields.Char(string="Employee Code", readonly=False)

