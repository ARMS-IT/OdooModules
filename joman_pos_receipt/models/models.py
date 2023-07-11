# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PosOrder(models.Model):
    _inherit = "pos.order"


    image = fields.Binary(string='Image')
    branch_company_id = fields.Many2one('res.company',string='Branch Company')

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        pos_session = self.env['pos.session'].browse(ui_order['pos_session_id'])
        if pos_session.config_id.branch_company_id:
            branch_company_id = pos_session.config_id.branch_company_id.id
            order_fields['branch_company_id'] = branch_company_id
        return order_fields


class PosConfigImage(models.Model):
    _inherit = 'pos.config'

    image = fields.Binary(string='Image')
    branch_company_id = fields.Many2one(
        'res.company',
        string='Branch Company',
        default=lambda self: self.env.user.company_id,
    )
    shop_cr_no = fields.Char(string='CR No')    
