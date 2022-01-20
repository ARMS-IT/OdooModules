# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

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
                name = name.split("/", 1)
                move.invoice_seq_num = name[1]

    #
    # def action_post(self):
    #     res = super(AccountMove, self).action_post()
    #     name = self.name
    #     if name !='Draft' or name !='/':
    #         name = name.split("/", 1)
    #         self.invoice_seq_nbr = name[1]
    #     return res
    #
    # def action_update_invoice_seq_nbr(self):
    #     name = self.name
    #     if name !='Draft' or name !='/':
    #         import re
    #         old_name = re.sub('\s+', ' ', name)
    #         print("old_name..",old_name)
    #         name = name.split("/", 1)
    #         self.invoice_seq_nbr = name[1]
    #     return True






