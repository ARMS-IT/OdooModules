# -*- coding: utf-8 -*-

from odoo import models, fields

class ResUser(models.Model):
    _inherit = "res.users"

    employee_type = fields.Selection([('user', 'User'), ('manager', 'Manager')], string="Employee Type")