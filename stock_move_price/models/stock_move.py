# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import pycompat
from odoo.tools.float_utils import float_round
from datetime import datetime

class StockMove(models.Model):
    _inherit = "stock.move"

    sale_price = fields.Float('Sale Price', compute='onchange_product')
    cost_price = fields.Float('Cost Price',compute='onchange_product')


#    @api.onchange('product_id', 'picking_type_id')
#    def onchange_product(self):
#        for rec in self:
#            if rec.product_id:
#                product = rec.product_id.with_context(lang=self._get_lang())
#                rec.sale_price = product.lst_price
#                rec.cost_price = product.standard_price


    @api.depends('product_id')
    def onchange_product(self):
        for rec in self:
            sale_price = 0.0
            cost_price = 0.0
            if rec.product_id:
                #product = rec.product_id.with_context(lang=self._get_lang())
                sale_price = rec.product_id.lst_price
                cost_price = rec.product_id.standard_price
            rec.sale_price = sale_price
            rec.cost_price = cost_price


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    sale_price = fields.Float('Sale Price', compute='_compute_price')
    cost_price = fields.Float('Cost Price', compute='_compute_price')
    total_price = fields.Float('Total Price', compute='_compute_price')

    @api.depends('move_id.sale_price','move_id.cost_price','qty_done')
    def _compute_price(self):
        for rec in self:
            rec.sale_price = rec.move_id.sale_price
            rec.cost_price = rec.move_id.cost_price
            rec.total_price = rec.move_id.cost_price*rec.qty_done

