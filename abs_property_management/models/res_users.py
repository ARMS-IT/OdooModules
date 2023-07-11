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

class Users(models.Model):
    _inherit = "res.users"

    @api.model
    def create(self, vals):
        result = super(Users, self).create(vals)
        buyer_group = result.has_group('abs_property_management.group_user_buyer')
        tenant_group = result.has_group('abs_property_management.group_user_tenant')
        if buyer_group == True:
            result.partner_id.user_is = 'buyer'
        if tenant_group == True:
            result.partner_id.user_is = 'tenant'
        return result

    def write(self,vals):
        result = super(Users, self).write(vals)
        buyer_group = self.has_group('abs_property_management.group_user_buyer')
        tenant_group = self.has_group('abs_property_management.group_user_tenant')
        if buyer_group == True:
            self.partner_id.user_is = 'buyer'
        if tenant_group == True:
            self.partner_id.user_is = 'tenant'
        return result
