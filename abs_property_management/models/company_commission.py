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

class CompanyCommission(models.Model):
    _name = "company.commission"
    _description = "Company Commission"


    channel_ids = fields.Many2one('crm.team', string="Commission Level")
    user_id = fields.Many2one('res.users',"Person name")
    percentage = fields.Float("Percentage(%)")
    product_template_id = fields.Many2one('product.template', string="Property Id")

    #Domain on 'user_id'
    @api.onchange('channel_ids')
    def onchange_channel_ids(self):
        domain = {}
        for record in self:
            if record.channel_ids.member_ids:
                members = []
                for member in record.channel_ids.member_ids:
                    members.append(member.id)
                if members:
                    domain['user_id'] =  [('id', 'in', members)]
            else:
                domain['user_id'] =  []
        return {'domain': domain}
