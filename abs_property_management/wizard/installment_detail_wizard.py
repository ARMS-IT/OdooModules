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
from odoo import api, fields,tools, models,_
from odoo.exceptions import ValidationError
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta

class InstallmentDetailWizard(models.TransientModel):
    _name = 'installment.detail.wizard'
    _description = "Installment Detail Wizard"

    property_id = fields.Many2one('product.template',"Property", default=lambda self: self.env.context.get('active_id'))
    property_price = fields.Float('Property Price')
    property_description = fields.Text("Property Description")
    installment = fields.Many2one('property.installment', string="Select Installment")
    fiscal_position_id = fields.Many2one('account.fiscal.position', oldname='fiscal_position', string='Fiscal Position')

    @api.onchange('property_id')
    def onchange_property_id(self):
        domain = {}
        for record in self:
            if record.property_id:
                property_obj = self.env['product.template'].search([('id','=',record.property_id.id)])
                if property_obj:
                    record.property_price = property_obj.property_price
                    record.property_description = property_obj.property_description
            if record.property_id.allowed_installments:
                available_installment_list = []
                for installment in record.property_id.allowed_installments:
                    if installment:
                        available_installment_list.append(installment.id)
                if available_installment_list:
                    domain['installment'] =  [('id', 'in', available_installment_list)]
                else:
                    domain['installment'] =  []
        return {'domain': domain}

    def create_property_installments_invoice(self):
        for record in self:
            if record.property_id:
                current_user = self.env.user
                partner_id = self.env.user.partner_id
                product_id = self.env['product.product'].search([('product_tmpl_id','=',self.property_id.id)])
                total_installment =  self.installment.installment
                price = self.property_price / total_installment
                ir_property_obj = self.env['ir.property']
                account_id = False
                if product_id.id:
                    account_id = product_id.property_account_income_id.id
                if not account_id:
                    inc_acc = ir_property_obj._get('property_account_income_categ_id', 'product.category')
                    account_id = self.fiscal_position_id.map_account(inc_acc).id if inc_acc else False
                due_date = date.today()
                invoice_date = date.today()
                invoice_count = 0
                for count in range(total_installment):
                    if count <= total_installment:
                        invoice_count += 1
                        invoice_obj = self.env['account.move']
                        invoice_obj.sudo().create({'partner_id'  : partner_id.id,
                                            'buyer_partner_id'  : partner_id.id,                                           
                                            'invoice_origin': self.property_id.id,
                                            'invoice_date':invoice_date,
                                            'invoice_date_due':due_date,
                                            'move_type': 'out_invoice',
                                            'invoice_line_ids': [(0,0,{
                                                                       'product_id': product_id.id,
                                                                       'name'      : product_id.name,
                                                                       'price_unit': price,
                                                                       'quantity'  : 1,
                                                                       'account_id': account_id,
                                                                      })],
                                           })
                        first_day = due_date
                        if first_day:
                            due_date = first_day + relativedelta(months=1)
                property_id = self.env['product.template'].sudo().search([('id','=',self.property_id.id)])
                property_id.sudo().write({'property_status': 'sold', 'current_property_user_id':current_user.id})
