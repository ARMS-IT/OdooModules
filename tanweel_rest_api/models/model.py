# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields
from odoo.tools.translate import _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"

    initial_amount = fields.Float(string="Initial Amount", readonly=True, copy=False)
    pay_txn_id = fields.Char(string="Payment transaction", readonly=True, copy=False)
    app_id = fields.Char(string="App ID", readonly=True, copy=False)
    loan_type_code = fields.Char(string="Loan Type Code", readonly=True, copy=False)
    pay_session_id = fields.Char(string="Payment Session", readonly=True, copy=False)
    pay_txn_datetime = fields.Datetime('Payment TXN Date',readonly=True,copy=False)
    fe_id = fields.Char(string="FE ID", readonly=True, copy=False)
