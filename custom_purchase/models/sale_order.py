# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.depends('order_line.price_total')
    def get_total_discount(self):
        for order in self:
            total_discount = 0.0
            for line in order.order_line:
                total_discount += line.price_unit * line.product_uom_qty * line.discount/100
            # total_discount_percentage = (total_discount / order.amount_untaxed) * 100
            order.update({
                'total_discount': total_discount,
            })

    total_discount = fields.Monetary("Total Discount", compute = get_total_discount, store=True)
    total_discount_percentage = fields.Float("Total Discount Percentage", compute = get_total_discount, store=True)