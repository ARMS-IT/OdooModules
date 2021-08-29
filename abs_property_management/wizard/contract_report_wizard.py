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
from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
import datetime

class ContractReport(models.TransientModel):
    _name = "contract.report.wizard"
    _description = "Contract Report"

    contract_id = fields.Many2one('property.contract', string="Contracts")
    start_date = fields.Date("Start date")
    end_date = fields.Date("End date")

    def check_report(self):
        data = {}
        data['form'] = self.read(['contract_id','start_date','end_date'])
        return self._print_report(data)

    def _print_report(self, data):
        return self.env.ref('abs_property_management.action_contract_report').report_action(self, data=data, config=False)

    def expiry_contracts(self):
        contract_list = []
        for record in self:
            if record.start_date and record.end_date:
                contract_ids = self.env['property.contract'].search([('end_date','>=',record.start_date),('end_date','<=',record.end_date)])
                for contract_id in contract_ids:
                    if contract_id:
                        contract_list.append(contract_id)
            return {
                    'name'     : _('Expiry Contracts'),
                    'type'     : 'ir.actions.act_window',
                    'domain'   : [('id','in',[x.id for x in contract_list])],
                    'view_mode': 'tree',
                    'res_model': 'property.contract',
                    'view_id'  : False,
                    'action'   : 'view_property_contract_tree',
                    'target'   : 'current'
                   }
