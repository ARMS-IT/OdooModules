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

class PropertyContract(models.Model):
    _name = "property.contract"
    _order = 'start_date'
    _description = "Property Contract"

    name = fields.Char("Contract Number")
    partner_id = fields.Many2one('res.partner',"Tenant Name", domain=([('user_is','=','tenant')]))
    tenancy_id = fields.Many2one('product.template',"Tenancy Name", domain=([('is_property','=',True)]))
    owner_name = fields.Char("Landlord")
    contract_type = fields.Many2one('contract.type',"Contract Type")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("Expiration Date")
    renewal_date = fields.Date("Contract Renewal Date")
    deposit = fields.Integer("Deposit", help="Tenancy Deposit")
    active_or_not = fields.Selection([('normal','Grey'),('done','Green'),('blocked','Red')], string='Active',default='normal', compute="compute_contract_is_active_or_not")

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
    def onchange_tenancy_id(self):
        for record in self:
            if record.tenancy_id:
                record.deposit = record.tenancy_id.deposit
                record.owner_name = record.tenancy_id.partner_id.name

    def compute_contract_is_active_or_not(self):
        for record in self:
            if str(record.start_date) <= str(date.today()) and str(record.end_date) >= str(date.today()):
                record.active_or_not = 'done'
            elif str(record.end_date) < str(date.today()):
                record.active_or_not = 'blocked'
            else:
                record.active_or_not = 'normal'

    #Create sequance number
    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].sudo().get('property.contract') or ' '
        vals['name'] = sequence
        result = super(PropertyContract, self).create(vals)
        contract_ids = self.env['property.contract'].search([])
        for contract_id in contract_ids:
            if contract_id.tenancy_id.id == vals['tenancy_id']:
                if ((str(vals['start_date']) and str(vals['end_date'])) > str((contract_id.start_date)) and str((vals['start_date']) and str(vals['end_date'])) < str((contract_id.end_date))) or ( (str((vals['start_date']) or str(vals['end_date'])) > str((contract_id.start_date))) and (str((vals['start_date']) or str(vals['end_date'])) < str((contract_id.end_date)))):
                    raise ValidationError('On same dates Contract exist on this property')
                else:
                    pass
        if result:
            today_date = date.today()
            tenant_history_obj = self.env['tenant.history'].create({'date'       : today_date,
                                                                    'tenant_id'  : result.partner_id.id,
                                                                    'tenancy_id' : result.tenancy_id.id,
                                                                    'start_date' : result.start_date,
                                                                    'end_date'   : result.end_date,
                                                                    'contract_id': result.id,
                                                                   })
        return result

    def write(self, vals):
        sequence = self.env['ir.sequence'].sudo().get('property.contract') or ' '
        vals['name'] = sequence
        result = super(PropertyContract, self).write(vals)
        start_date = str(vals.get('start_date'))
        end_date = str(vals.get('end_date'))
        tenancy_id = vals.get('tenancy_id')
        contract_ids = self.env['property.contract'].search([])
        for contract_id in contract_ids:
            if contract_id.tenancy_id.id == tenancy_id:
                if ((start_date and end_date) > (contract_id.start_date) and (start_date and end_date) < (contract_id.end_date)) or ( ((start_date or end_date) > (contract_id.start_date)) and ((start_date or end_date) < (contract_id.end_date)) ):
                    raise ValidationError('Already Contract exist on this property')
                else:
                    pass
        if result:
            tenant_history_id = self.env['tenant.history'].search([('contract_id','=',self.id)])
            if tenant_history_id:
                tenant_history_id.write({
                                         'tenant_id' : self.partner_id.id,
                                         'tenancy_id': self.tenancy_id.id,
                                         'start_date': self.start_date,
                                         'end_date'  : self.end_date,
                                        })
        return result

    def _send_customer_contract_renewal_date_email(self):
        contract_ids = self.env['property.contract'].search([('renewal_date','=',date.today())])
        if contract_ids:
            for contract_id in contract_ids:
                if contract_id.partner_id:
                    end_date = contract_id.end_date
                    email_body = "<font size=""2""> <p> Hello, </p> <p> We’d like to take this opportunity to thank you for your support over the past some months. We value all contributions to our company, and memberships make up the lifeblood of our organization. Your involvement is extremely important to us and very much appreciated.</p> <p> That said, we know you’re busy and just wanted to take this time to remind you that your contract with our company will expire on {0}.</p> <p> We hope that you’ll take this time to renew your contract and remain a part of our community.</p> </font>".format(end_date)
                    if email_body:
                        email_subject = "This email is for renew a contract"
                        mail = {
                                'subject'  : email_subject,
                                'email_to' : contract_id.partner_id.name,
                                'body_html': email_body
                               }
                        mail_create = self.env['mail.mail'].create(mail)
                        if mail_create:
                            mail_create.send()


class ContractType(models.Model):
    _name = "contract.type"
    _description = "Contract Type"

    name = fields.Char("Name")
