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

class ContractDetailWizard(models.TransientModel):
    _name = 'contract.detail.wizard'
    _description = "Contract Detail Wizard"

    partner_id = fields.Many2one('res.partner',"Tenant Name", domain=([('user_is','=','tenant')]), default=lambda self: self.env.user.partner_id.id)
    tenancy_id = fields.Many2one('product.template',"Tenancy Name", domain=([('is_property','=',True)]), default=lambda self: self.env.context.get('active_id'))
    owner_name = fields.Char("Landlord")
    contract_type = fields.Many2one('contract.type',"Contract Type")
    deposit = fields.Integer("Deposit", help="Tenancy Deposit")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("Expiration Date")
    renewal_date = fields.Date("Contract Renewal Date")

    @api.onchange('start_date')
    def onchange_start_date(self):
        for record in self:
            if record.end_date:
                if record.start_date > record.end_date:
                    raise ValidationError('Please enter valid date')

    @api.onchange('end_date')
    def onchange_end_date(self):
        for record in self:
            if record.start_date:
                if record.end_date < record.start_date:
                    raise ValidationError('Please enter valid date')

    @api.onchange('renewal_date')
    def onchange_renewal_date(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.start_date <= record.renewal_date <= record.end_date:
                    pass
                else:
                    raise ValidationError('Please enter valid date')

    @api.onchange('tenancy_id')
    def onchange_wizard_tenancy_id(self):
        for record in self:
            if record.tenancy_id:
                tenancy_id = self.env['product.template'].sudo().search([('id','=',record.tenancy_id.id)])
                if tenancy_id:
                    record.deposit = tenancy_id.deposit
                    record.owner_name = tenancy_id.partner_id.name

    def create_property_contract(self):
        for record in self:
            if record:
                current_user = self.env.user
                tenancy_id = self.env['product.template'].sudo().search([('id','=',self.tenancy_id.id)])
                contract_id = self.env['property.contract'].sudo().create({ 'partner_id'  : self.partner_id.id,
                                                                     'tenancy_id'  : self.tenancy_id.id,
                                                                     'deposit'     : tenancy_id.deposit,
                                                                     'owner_name'  : tenancy_id.partner_id.name,
                                                                     'contract_type': self.contract_type.id,
                                                                     'start_date'  : self.start_date,
                                                                     'end_date'    : self.end_date,
                                                                     'renewal_date': self.renewal_date,
                                                                    })
                if contract_id:
                    tenancy_id.sudo().write({
                                             'property_status':'booked', 
                                             'current_property_user_id':current_user.id
                                           })

