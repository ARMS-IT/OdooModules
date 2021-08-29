# -*- coding: utf-8 -*-

from odoo import fields, models

class CrmLead(models.Model):
    _inherit= "crm.lead"

    industry = fields.Char(string="Industry")
    organization_size = fields.Char(string="Organization Size")
    subject = fields.Char(string="Subject")