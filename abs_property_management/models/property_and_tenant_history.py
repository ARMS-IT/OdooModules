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
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date

class TenantHistory(models.Model):
    _name = "tenant.history"
    _description = "Tenant History"

    tenant_id = fields.Many2one('res.partner',"Tenant", domain=([('user_is','=','tenant')]))
    tenancy_id = fields.Many2one('product.template',"Tenancy Name", domain=([('is_property','=',True)]))
    date = fields.Date("Date")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    rent = fields.Float("Rent")
    status = fields.Selection([('new','New'),('in_progress','In Progress'),('finish','Finish')], compute= 'compute_status')
    contract_id = fields.Many2one('property.contract', "Contract")
    fiscal_position_id = fields.Many2one('account.fiscal.position', oldname='fiscal_position', string='Fiscal Position')
    invoice_id = fields.Many2one('account.move','Invoice Number')

    def compute_status(self):
        for record in self:
            if str(record.start_date) > str(date.today()):
                record.status = 'new'
            elif str(record.start_date) < str(date.today()) and str(record.end_date) > str(date.today()):
                record.status = 'in_progress'
            elif str(record.end_date) < str(date.today()):
                record.status = 'finish'

    @api.model
    def create(self,vals):
        if vals['tenancy_id']:
            tenancy_id = self.env['product.template'].search([('id','=',vals['tenancy_id'])])
            tenancy_rent = tenancy_id.property_price
            vals.update({'rent':tenancy_rent})
        result = super(TenantHistory, self).create(vals)
        return result

    def write(self,vals):
        if vals.get('tenancy_id'):
            tenancy_id = self.env['product.template'].search([('id','=',vals.get('tenancy_id'))])
            tenancy_rent = tenancy_id.property_price
            vals.update({'rent':tenancy_rent})
        result = super(TenantHistory, self).write(vals)
        return result

    def create_property_rent_invoice(self):
        for record in self:
            if record.tenancy_id:
                partner_id = self.tenant_id
                product_id = self.env['product.product'].search([('product_tmpl_id','=',self.tenancy_id.id)])
                price = self.tenancy_id.property_price
                ir_property_obj = self.env['ir.property']
                account_id = False
                if product_id.id:
                    account_id = product_id.property_account_income_id.id
                if not account_id:
                    inc_acc = ir_property_obj._get('property_account_income_categ_id', 'product.category')
                    account_id = self.fiscal_position_id.map_account(inc_acc).id if inc_acc else False
                invoice_date = date.today()
                due_date = self.end_date
                invoice_obj = self.env['account.move']
                invoice_id = invoice_obj.create({'partner_id'  : partner_id.id,
                                    'tenant_partner_id'  : partner_id.id,
                                    'invoice_origin': self.tenancy_id.name,
                                    'invoice_date': invoice_date,
                                    'invoice_date_due': due_date,
                                    'move_type' : 'out_invoice',
                                    'invoice_line_ids': [(0,0,{
                                                               'product_id': product_id.id,
                                                               'name'      : product_id.name,
                                                               'price_unit': price,
                                                               'quantity'  : 1,
                                                               'account_id': account_id,
                                                              })],
                                 })
                if invoice_id:
                    self.write({'invoice_id': invoice_id.id})
