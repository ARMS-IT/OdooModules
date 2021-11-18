# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class EmployeeRegion(models.Model):
    _name = 'employee.region'
    _description = 'Employee Region'
    _order = 'name'

    name = fields.Char(string='Name', help="Name",required=True)
    region_line_ids = fields.One2many('employee.region.line', 'region_id',"Region Line")

    _sql_constraints = [
        ('unique_region_name', 'unique (name)', 'This name already exists')
    ]

class EmployeeRegionLine(models.Model):
    _name = 'employee.region.line'
    _description = 'Employee Region Line'
    _order = 'name'

    name = fields.Char(string='Email')
    employee_id = fields.Many2one('hr.employee','Employee',required=True)
    region_id = fields.Many2one('employee.region','Region',required=True)

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if not self.employee_id:
            self.name = False
        else:
            self.name = self.employee_id.work_email

