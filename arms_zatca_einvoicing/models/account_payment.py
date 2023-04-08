# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    @api.model
    def default_get(self, fields_list):
        # OVERRIDE
        res = super().default_get(fields_list)
        if self._context.get('active_model') == 'account.move':
            move_rec = self.env['account.move'].browse(self._context.get('active_ids', []))
            res['payment_date'] = move_rec.invoice_time.date()
        return res

    # def _create_payment_vals_from_wizard(self):
    #     # OVERRIDE
    #     payment_vals = super()._create_payment_vals_from_wizard()
    #     if self._context.get('active_model') == 'account.move':
    #         move_rec = self.env['account.move'].browse(self._context.get('active_ids', []))
    #         print("$$$$$$$",payment_vals)
    #         payment_vals['date'] = move_rec.invoice_time.date()
    #     prinhgh
    #     return payment_vals
    #
    # def _create_payment_vals_from_batch(self):
    #     # OVERRIDE
    #     batch_values = super()._create_payment_vals_from_batch()
    #     if self._context.get('active_model') == 'account.move':
    #         move_rec = self.env['account.move'].browse(self._context.get('active_ids', []))
    #         batch_values['date'] = move_rec.invoice_time.date()
    #     return batch_values
