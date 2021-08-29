# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-Today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)

from functools import lru_cache

class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    buyer_partner_id = fields.Many2one('res.partner', string='Buyer', readonly=True, domain=[('user_is', '=', 'buyer')])
    tenant_partner_id = fields.Many2one('res.partner', string='Tenant', readonly=True, domain=[('user_is', '=',' tenant')])


    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", move.buyer_partner_id as buyer_partner_id, move.tenant_partner_id as tenant_partner_id"

    def _sub_select(self):
        return super(AccountInvoiceReport, self)._sub_select() + ", move.buyer_partner_id as buyer_partner_id, move.tenant_partner_id as tenant_partner_id"

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ", move.buyer_partner_id, move.tenant_partner_id"
