# -*- coding: utf-8 -*-

from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    region_id = fields.Many2one('employee.region', string='Region')

class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    region_id = fields.Many2one('employee.region', string='Region')
