# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import re

class AccountMove(models.Model):
    _inherit = 'account.move'
    _order = 'invoice_seq_num desc, date desc, id desc'

    invoice_seq_num = fields.Char(string="INV NUM", store=True, readonly=False,
        compute='_compute_invoice_seq_num')

    @api.depends('name')
    def _compute_invoice_seq_num(self):
        for move in self:
            name = move.name
            if name == False or name== '' or name == 'Draft' or name == '/':
                move.invoice_seq_num = False
            else:
                # name = name.split("/", 1)
                name = re.split(r'(^[^\d]+)', name)[1:]
                move.invoice_seq_num = name[1]







