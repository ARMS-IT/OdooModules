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

class PropertyMaintenance(models.Model):
    _name = "property.maintenance"
    _order = 'date'
    _description = "Property Maintenance"

    name = fields.Many2one('product.template',"Property name", domain=([('is_property','=',True)]))
    date = fields.Date("Date")
    maintenance_type = fields.Many2one('maintenance.type', "Maintenance Type")
    action = fields.Selection([('renew','Renew'),('repair','Repair')])
    state = fields.Selection([('new','New'),('in_progress','In Progress'),('done','Done')], compute="compute_state")
    assign_to = fields.Many2one('res.partner',"Assign To")
    cost = fields.Float("Cost")
    note = fields.Text("Notes")
    fiscal_position_id = fields.Many2one('account.fiscal.position',"Fiscal Position")
    invoice_id = fields.Many2one('account.move',"Invoice Number")

    def compute_state(self):
        for record in self:
            if record.invoice_id.state == 'open':
                record.state = 'in_progress'
            elif record.invoice_id.state == 'paid':
                record.state = 'done'
            else:
                record.state = 'new'

    def create_invoice(self):
        for record in self:
            if record.assign_to:
                ir_property_obj = self.env['ir.property']
                invoice_date = date.today()
                product_name = record.name.name
                product_id = self.env['product.product'].search([('product_tmpl_id','=',self.name.id)])
                description = str(record.maintenance_type.name) + str(" - ") + str(record.action)
                account_id = False
                if record.name.id:
                    account_id = record.name.property_account_income_id.id
                if not account_id:
                    inc_acc = ir_property_obj._get('property_account_income_categ_id', 'product.category')
                    account_id = self.fiscal_position_id.map_account(inc_acc).id if inc_acc else False
                invoice_obj = self.env['account.move']
                invoice_id = invoice_obj.create({'partner_id': record.assign_to.id,
                                                 'invoice_origin': product_name,
                                                 'invoice_date' :invoice_date,
                                                 'move_type': 'out_invoice',
                                                 'invoice_line_ids': [(0,0,{
                                                                      'product_id': product_id.id,
                                                                      'name'      : description,
                                                                      'price_unit': record.cost,
                                                                      'account_id': account_id,
                                                                     })],
                                                })
                self.write({'invoice_id':invoice_id.id})


class MaintenanceType(models.Model):
    _name = "maintenance.type"
    _description = "Maintenance Type"

    name = fields.Char("Name")
