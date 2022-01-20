# -*- coding: utf-8 -*-

from odoo import models, fields, api


# class altayibat_pos_receipt(models.Model):
#     _name = 'altayibat_pos_receipt.altayibat_pos_receipt'
#     _description = 'altayibat_pos_receipt.altayibat_pos_receipt'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100


class PosOrder(models.Model):
    _inherit = "pos.order"

    branch_company_id = fields.Many2one(
        'res.company',
        string='Branch Company',
    )

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        pos_session = self.env['pos.session'].browse(ui_order['pos_session_id'])
        if pos_session.config_id.branch_company_id:
            branch_company_id = pos_session.config_id.branch_company_id.id
            print("%%%%%branch_company_id%%%%",branch_company_id)
            order_fields['branch_company_id'] = branch_company_id
        return order_fields

    # def _export_for_ui(self, order):
    #     result = super(PosOrder, self)._export_for_ui(order)
    #     print("&&&&&&&&&&",order)
    #     print("&&&&&&&&&&",order.session_id)
    #     print("&&&&&&&&&&",order.config_id)
    #     result.update({
    #         'branch_company_id': order.config_id.id,
    #     })
    #     return result
